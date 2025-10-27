"""
Test Script toàn diện cho Backend API

Kiểm tra tất cả endpoints và chức năng chính của backend.
Chạy script này để đảm bảo backend hoạt động đúng trước khi deploy.

Usage:
    python test_api_comprehensive.py
    
hoặc:
    uv run python test_api_comprehensive.py
"""

import requests
import json
from typing import Dict, Any, List

# Base URL của API
BASE_URL = "http://localhost:8000"

# Màu sắc cho console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str, passed: bool, message: str = ""):
    """In kết quả test với màu sắc"""
    if passed:
        print(f"{Colors.GREEN}✓{Colors.ENDC} {name}")
        if message:
            print(f"  {Colors.BLUE}→{Colors.ENDC} {message}")
    else:
        print(f"{Colors.RED}✗{Colors.ENDC} {name}")
        if message:
            print(f"  {Colors.RED}→{Colors.ENDC} {message}")


def test_health_check() -> bool:
    """Test 1: Health Check - Server có chạy không"""
    print(f"\n{Colors.BOLD}=== Test 1: Health Check ==={Colors.ENDC}")
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200 and "success" in response.json()
        print_test("GET /", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("GET /", False, f"Lỗi: {str(e)}")
        return False


def test_chat_basic() -> bool:
    """Test 2: Chat Basic - NLP có hoạt động không"""
    print(f"\n{Colors.BOLD}=== Test 2: Chat Basic (NLP) ==={Colors.ENDC}")
    try:
        data = {"message": "Điểm chuẩn ngành Kiến trúc"}
        response = requests.post(f"{BASE_URL}/chat", json=data)
        result = response.json()
        
        passed = (
            response.status_code == 200 and
            "intent" in result and
            "confidence" in result and
            "entities" in result
        )
        
        if passed:
            intent = result.get("intent", "N/A")
            conf = result.get("confidence", 0)
            entities_count = len(result.get("entities", []))
            print_test(
                "POST /chat", 
                True, 
                f"Intent: {intent}, Độ tin cậy: {conf:.2f}, {entities_count} entities"
            )
        else:
            print_test("POST /chat", False, f"Response không đúng format")
        
        return passed
    except Exception as e:
        print_test("POST /chat", False, f"Lỗi: {str(e)}")
        return False


def test_chat_context() -> bool:
    """Test 3: Chat Context - Context management"""
    print(f"\n{Colors.BOLD}=== Test 3: Chat Context Management ==={Colors.ENDC}")
    session_id = "test_session_123"
    
    # Test Reset
    try:
        data = {"action": "reset", "session_id": session_id}
        response = requests.post(f"{BASE_URL}/chat/context", json=data)
        passed_reset = response.status_code == 200 and response.json().get("success")
        print_test("Context Reset", passed_reset)
    except Exception as e:
        print_test("Context Reset", False, f"Lỗi: {str(e)}")
        passed_reset = False
    
    # Test Get
    try:
        data = {"action": "get", "session_id": session_id}
        response = requests.post(f"{BASE_URL}/chat/context", json=data)
        passed_get = response.status_code == 200 and "context" in response.json()
        print_test("Context Get", passed_get)
    except Exception as e:
        print_test("Context Get", False, f"Lỗi: {str(e)}")
        passed_get = False
    
    return passed_reset and passed_get


def test_data_endpoints() -> bool:
    """Test 4: Data Endpoints - Các endpoint tra cứu dữ liệu"""
    print(f"\n{Colors.BOLD}=== Test 4: Data Endpoints ==={Colors.ENDC}")
    
    endpoints_to_test = [
        ("GET /nganh", f"{BASE_URL}/nganh"),
        ("GET /nganh?q=kiến trúc", f"{BASE_URL}/nganh?q=kiến trúc"),
        ("GET /diem", f"{BASE_URL}/diem"),
        ("GET /hocphi", f"{BASE_URL}/hocphi"),
        ("GET /hocbong", f"{BASE_URL}/hocbong"),
        ("GET /chi-tieu", f"{BASE_URL}/chi-tieu"),
        ("GET /lich", f"{BASE_URL}/lich"),
        ("GET /kenh-nop", f"{BASE_URL}/kenh-nop"),
        ("GET /dieu-kien", f"{BASE_URL}/dieu-kien"),
    ]
    
    all_passed = True
    for name, url in endpoints_to_test:
        try:
            response = requests.get(url)
            result = response.json()
            passed = response.status_code == 200 and "items" in result
            count = len(result.get("items", []))
            print_test(name, passed, f"Trả về {count} kết quả")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(name, False, f"Lỗi: {str(e)}")
            all_passed = False
    
    return all_passed


def test_suggest_majors() -> bool:
    """Test 5: Suggest Majors - Gợi ý ngành theo điểm"""
    print(f"\n{Colors.BOLD}=== Test 5: Gợi ý ngành theo điểm ==={Colors.ENDC}")
    try:
        data = {
            "score": 25.5,
            "score_type": "chuan",
            "year": "2025"
        }
        response = requests.post(f"{BASE_URL}/goiy", json=data)
        result = response.json()
        
        passed = response.status_code == 200 and "items" in result
        if passed:
            count = len(result.get("items", []))
            print_test("POST /goiy", True, f"Gợi ý {count} ngành phù hợp")
        else:
            print_test("POST /goiy", False, f"Response không đúng format")
        
        return passed
    except Exception as e:
        print_test("POST /goiy", False, f"Lỗi: {str(e)}")
        return False


def test_error_handling() -> bool:
    """Test 6: Error Handling - Kiểm tra xử lý lỗi"""
    print(f"\n{Colors.BOLD}=== Test 6: Error Handling ==={Colors.ENDC}")
    
    # Test empty message
    try:
        data = {"message": ""}
        response = requests.post(f"{BASE_URL}/chat", json=data)
        passed = response.status_code == 422  # Validation error
        print_test("Empty message validation", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Empty message validation", False, f"Lỗi: {str(e)}")
        return False
    
    # Test invalid action in context
    try:
        data = {"action": "invalid_action", "session_id": "test"}
        response = requests.post(f"{BASE_URL}/chat/context", json=data)
        passed = response.status_code == 422  # Validation error
        print_test("Invalid action validation", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Invalid action validation", False, f"Lỗi: {str(e)}")
        return False
    
    return True


def run_all_tests():
    """Chạy tất cả tests và tổng hợp kết quả"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}TEST SUITE - Backend API Comprehensive Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Đảm bảo server đang chạy: uvicorn main:app --reload{Colors.ENDC}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Chat Basic", test_chat_basic),
        ("Chat Context", test_chat_context),
        ("Data Endpoints", test_data_endpoints),
        ("Suggest Majors", test_suggest_majors),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n{Colors.RED}Lỗi không mong đợi trong test {name}: {str(e)}{Colors.ENDC}")
            results.append((name, False))
    
    # Tổng kết
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}TỔ HỢPEDU KẾT QUẢ{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = f"{Colors.GREEN}PASSED{Colors.ENDC}" if passed else f"{Colors.RED}FAILED{Colors.ENDC}"
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BOLD}Kết quả: {passed_count}/{total_count} tests passed{Colors.ENDC}")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ TẤT CẢ TESTS ĐỀU PASS! Backend sẵn sàng.{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Có {total_count - passed_count} tests failed. Cần kiểm tra lại.{Colors.ENDC}")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test bị ngắt bởi user.{Colors.ENDC}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Lỗi fatal: {str(e)}{Colors.ENDC}")
        exit(1)

