import os
import re
import csv
import json
import math
import unicodedata
from typing import List, Dict, Tuple, Any, Set

try:
	from underthesea import word_tokenize
except Exception:  # fallback if underthesea is not installed
	def word_tokenize(text: str, format=None):
		return text.split()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

DEFAULT_INTENT_THRESHOLD = 0.35  # lower because TF-IDF cosine is stricter than Jaccard

# Minimal Vietnamese stopword set (extendable)
VI_STOPWORDS: Set[str] = {
	"là", "làm", "và", "hoặc", "nhưng", "thì", "lúc", "khi", "ở", "của",
	"cho", "với", "đến", "tới", "từ", "có", "được", "nhé", "ạ", "à", "ư",
	"mình", "bạn", "xin", "chào", "ơi", "giúp", "hỏi", "cho", "xem", "bao",
}


class NLPPipeline:
	def __init__(self, data_dir: str = DATA_DIR, intent_threshold: float = DEFAULT_INTENT_THRESHOLD) -> None:
		self.data_dir = data_dir
		self.intent_threshold = intent_threshold
		self.syn_map = self._load_synonyms(os.path.join(data_dir, 'synonym.csv'))
		self.intent_samples = self._load_intent_samples(os.path.join(data_dir, 'intent.csv'))
		self.entity_patterns = self._load_entity_patterns(os.path.join(data_dir, 'entity.json'))
		# Build TF-IDF centroid per intent
		self.idf: Dict[str, float] = {}
		self.intent_centroids: Dict[str, Dict[str, float]] = {}
		self._build_intent_centroids()

	# ---------- Loaders ----------
	def _load_synonyms(self, path: str) -> Dict[str, str]:
		mapping: Dict[str, str] = {}
		if not os.path.isfile(path):
			return mapping
		with open(path, newline='', encoding='utf-8') as f:
			reader = csv.reader(f)
			_ = next(reader, None)  # header if present
			for row in reader:
				if len(row) < 2:
					continue
				src = self._normalize_text(row[0])
				dst = self._normalize_text(row[1])
				if src and dst:
					mapping[src] = dst
		return mapping

	def _load_intent_samples(self, path: str) -> Dict[str, List[List[str]]]:
		intent_to_samples: Dict[str, List[List[str]]] = {}
		with open(path, newline='', encoding='utf-8') as f:
			reader = csv.DictReader(f)
			for r in reader:
				utt = self._normalize_text(r.get('utterance') or '')
				intent = (r.get('intent') or '').strip()
				if not utt or not intent:
					continue
				toks = self._tokenize_and_map(utt)
				intent_to_samples.setdefault(intent, []).append(toks)
		return intent_to_samples

	def _load_entity_patterns(self, path: str) -> List[Tuple[str, str]]:
		patterns: List[Tuple[str, str]] = []
		if not os.path.isfile(path):
			return patterns
		with open(path, 'r', encoding='utf-8') as f:
			data = json.load(f)
			for item in data:
				label = (item.get('label') or '').strip()
				pat = self._normalize_text(item.get('pattern') or '')
				if label and pat:
					patterns.append((label, pat))
		return patterns

	# ---------- Preprocess ----------
	def _normalize_text(self, text) -> str:
		if not isinstance(text, str):
			text = str(text) if text is not None else ""
		text = text.lower().strip()
		text = unicodedata.normalize('NFC', text)
		text = re.sub(r"[^\w\sáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]", " ", text)
		text = re.sub(r"\s+", " ", text).strip()
		return text

	def _tokenize_and_map(self, text: str) -> List[str]:
		norm = self._normalize_text(text)
		try:
			raw = word_tokenize(norm, format='text')
			toks = raw.split()
		except Exception:
			toks = norm.split()
		mapped = [self.syn_map.get(tok, tok) for tok in toks]
		# remove stopwords
		filtered = [t for t in mapped if t not in VI_STOPWORDS]
		return filtered

	# ---------- TF-IDF utilities ----------
	def _compute_idf(self, samples: List[List[str]]) -> Dict[str, float]:
		df: Dict[str, int] = {}
		n_docs = len(samples)
		for toks in samples:
			seen = set(toks)
			for t in seen:
				df[t] = df.get(t, 0) + 1
		idf: Dict[str, float] = {}
		for t, c in df.items():
			idf[t] = math.log((1 + n_docs) / (1 + c)) + 1.0
		return idf

	def _tf(self, toks: List[str]) -> Dict[str, float]:
		counts: Dict[str, int] = {}
		for t in toks:
			counts[t] = counts.get(t, 0) + 1
		total = float(len(toks)) or 1.0
		return {t: c / total for t, c in counts.items()}

	def _tfidf_vec(self, toks: List[str], idf: Dict[str, float]) -> Dict[str, float]:
		tf = self._tf(toks)
		vec = {t: tf[t] * idf.get(t, 0.0) for t in tf}
		norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
		return {t: v / norm for t, v in vec.items()}

	def _centroid(self, vecs: List[Dict[str, float]]) -> Dict[str, float]:
		agg: Dict[str, float] = {}
		for v in vecs:
			for k, val in v.items():
				agg[k] = agg.get(k, 0.0) + val
		norm = math.sqrt(sum(v * v for v in agg.values())) or 1.0
		return {k: v / norm for k, v in agg.items()}

	def _cosine(self, a: Dict[str, float], b: Dict[str, float]) -> float:
		# iterate smaller vector
		if len(a) > len(b):
			a, b = b, a
		s = 0.0
		for k, va in a.items():
			vb = b.get(k)
			if vb is not None:
				s += va * vb
		return s

	def _build_intent_centroids(self) -> None:
		# Flatten all samples to compute global IDF
		all_samples: List[List[str]] = []
		for samples in self.intent_samples.values():
			all_samples.extend(samples)
		self.idf = self._compute_idf(all_samples) if all_samples else {}
		centroids: Dict[str, Dict[str, float]] = {}
		for intent, samples in self.intent_samples.items():
			vecs = [self._tfidf_vec(s, self.idf) for s in samples]
			centroids[intent] = self._centroid(vecs) if vecs else {}
		self.intent_centroids = centroids

	# ---------- Intent ----------
	def detect_intent(self, text: str) -> Tuple[str, float]:
		q_tokens = self._tokenize_and_map(text)
		q_vec = self._tfidf_vec(q_tokens, self.idf)
		best_intent = ''
		best_score = 0.0
		for intent, centroid in self.intent_centroids.items():
			# prefer intents starting with 'hoi_'
			boost = 1.05 if intent.startswith('hoi_') else 1.0
			score = self._cosine(q_vec, centroid) * boost
			if score > best_score:
				best_score = score
				best_intent = intent
		if best_score >= self.intent_threshold:
			return best_intent, best_score
		return 'fallback', best_score

	# ---------- Entities ----------
	def extract_entities(self, text: str) -> List[Dict[str, Any]]:
		norm = self._normalize_text(text)
		found: List[Dict[str, Any]] = []
		for label, pat in self.entity_patterns:
			if pat and pat in norm:
				found.append({"label": label, "text": pat})
		return found

	# ---------- Public ----------
	def analyze(self, text: str) -> Dict[str, Any]:
		intent, score = self.detect_intent(text)
		entities = self.extract_entities(text)
		return {"intent": intent, "score": score, "entities": entities}
