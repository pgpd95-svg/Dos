import requests
import sys
from datetime import datetime, date
import json

class BudgetTrackerAPITester:
    def __init__(self, base_url="https://5b2bea35-7922-4614-9632-ff3c713ccb2c.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_items = {
            'categories': [],
            'transactions': [],
            'budgets': []
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: {len(response_data)} items returned")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_create_categories(self):
        """Test creating categories"""
        categories_to_create = [
            {"name": "Food", "color": "#FF6B6B", "type": "expense"},
            {"name": "Transport", "color": "#4ECDC4", "type": "expense"},
            {"name": "Entertainment", "color": "#45B7D1", "type": "expense"},
            {"name": "Salary", "color": "#96CEB4", "type": "income"},
            {"name": "Freelance", "color": "#FFEAA7", "type": "income"}
        ]
        
        for category_data in categories_to_create:
            success, response = self.run_test(
                f"Create Category - {category_data['name']}",
                "POST",
                "categories",
                200,
                data=category_data
            )
            if success and 'id' in response:
                self.created_items['categories'].append(response)
        
        return len(self.created_items['categories']) > 0

    def test_get_categories(self):
        """Test getting all categories"""
        success, response = self.run_test(
            "Get All Categories",
            "GET",
            "categories",
            200
        )
        return success

    def test_get_categories_by_type(self):
        """Test getting categories by type"""
        success1, _ = self.run_test(
            "Get Income Categories",
            "GET",
            "categories/income",
            200
        )
        success2, _ = self.run_test(
            "Get Expense Categories",
            "GET",
            "categories/expense",
            200
        )
        return success1 and success2

    def test_create_transactions(self):
        """Test creating transactions"""
        if not self.created_items['categories']:
            print("❌ No categories available for transaction testing")
            return False

        expense_categories = [cat for cat in self.created_items['categories'] if cat['type'] == 'expense']
        income_categories = [cat for cat in self.created_items['categories'] if cat['type'] == 'income']

        transactions_to_create = []
        
        # Add expense transactions
        if expense_categories:
            transactions_to_create.extend([
                {
                    "type": "expense",
                    "amount": 25.50,
                    "category_id": expense_categories[0]['id'],
                    "description": "Lunch at restaurant",
                    "date": date.today().isoformat(),
                    "currency": "USD"
                },
                {
                    "type": "expense", 
                    "amount": 15.00,
                    "category_id": expense_categories[1]['id'] if len(expense_categories) > 1 else expense_categories[0]['id'],
                    "description": "Bus fare",
                    "date": date.today().isoformat(),
                    "currency": "USD"
                }
            ])

        # Add income transactions
        if income_categories:
            transactions_to_create.extend([
                {
                    "type": "income",
                    "amount": 3000.00,
                    "category_id": income_categories[0]['id'],
                    "description": "Monthly salary",
                    "date": date.today().isoformat(),
                    "currency": "USD"
                }
            ])

        for transaction_data in transactions_to_create:
            success, response = self.run_test(
                f"Create Transaction - {transaction_data['description']}",
                "POST",
                "transactions",
                200,
                data=transaction_data
            )
            if success and 'id' in response:
                self.created_items['transactions'].append(response)

        return len(self.created_items['transactions']) > 0

    def test_get_transactions(self):
        """Test getting transactions"""
        success1, _ = self.run_test(
            "Get All Transactions",
            "GET",
            "transactions",
            200
        )
        success2, _ = self.run_test(
            "Get Income Transactions",
            "GET",
            "transactions/income",
            200
        )
        success3, _ = self.run_test(
            "Get Expense Transactions",
            "GET",
            "transactions/expense",
            200
        )
        return success1 and success2 and success3

    def test_create_budgets(self):
        """Test creating budgets"""
        expense_categories = [cat for cat in self.created_items['categories'] if cat['type'] == 'expense']
        
        if not expense_categories:
            print("❌ No expense categories available for budget testing")
            return False

        budgets_to_create = [
            {
                "category_id": expense_categories[0]['id'],
                "amount": 200.00,
                "period": "monthly",
                "currency": "USD"
            }
        ]

        if len(expense_categories) > 1:
            budgets_to_create.append({
                "category_id": expense_categories[1]['id'],
                "amount": 100.00,
                "period": "weekly",
                "currency": "USD"
            })

        for budget_data in budgets_to_create:
            success, response = self.run_test(
                f"Create Budget for Category",
                "POST",
                "budgets",
                200,
                data=budget_data
            )
            if success and 'id' in response:
                self.created_items['budgets'].append(response)

        return len(self.created_items['budgets']) > 0

    def test_get_budgets(self):
        """Test getting budgets"""
        success1, _ = self.run_test(
            "Get All Budgets",
            "GET",
            "budgets",
            200
        )
        success2, _ = self.run_test(
            "Get Monthly Budgets",
            "GET",
            "budgets/monthly",
            200
        )
        return success1 and success2

    def test_budget_overview(self):
        """Test budget overview endpoint"""
        success1, _ = self.run_test(
            "Get Monthly Budget Overview",
            "GET",
            "budget-overview/monthly",
            200
        )
        success2, _ = self.run_test(
            "Get Weekly Budget Overview",
            "GET",
            "budget-overview/weekly",
            200
        )
        return success1 and success2

    def test_analytics(self):
        """Test analytics endpoints"""
        success, _ = self.run_test(
            "Get Spending by Category",
            "GET",
            "analytics/spending-by-category",
            200,
            params={"period": "monthly"}
        )
        return success

    def test_settings(self):
        """Test settings endpoints"""
        success1, response = self.run_test(
            "Get Settings",
            "GET",
            "settings",
            200
        )
        
        success2, _ = self.run_test(
            "Update Settings",
            "PUT",
            "settings",
            200,
            data={"default_currency": "EUR"}
        )
        
        # Reset back to USD
        success3, _ = self.run_test(
            "Reset Settings to USD",
            "PUT",
            "settings",
            200,
            data={"default_currency": "USD"}
        )
        
        return success1 and success2 and success3

    def test_delete_operations(self):
        """Test delete operations"""
        success_count = 0
        
        # Delete a transaction if available
        if self.created_items['transactions']:
            transaction_id = self.created_items['transactions'][0]['id']
            success, _ = self.run_test(
                "Delete Transaction",
                "DELETE",
                f"transactions/{transaction_id}",
                200
            )
            if success:
                success_count += 1

        # Delete a budget if available
        if self.created_items['budgets']:
            budget_id = self.created_items['budgets'][0]['id']
            success, _ = self.run_test(
                "Delete Budget",
                "DELETE",
                f"budgets/{budget_id}",
                200
            )
            if success:
                success_count += 1

        return success_count > 0

def main():
    print("🚀 Starting Budget Tracker API Tests")
    print("=" * 50)
    
    tester = BudgetTrackerAPITester()
    
    # Run all tests
    test_results = []
    
    test_results.append(("Root Endpoint", tester.test_root_endpoint()))
    test_results.append(("Create Categories", tester.test_create_categories()))
    test_results.append(("Get Categories", tester.test_get_categories()))
    test_results.append(("Get Categories by Type", tester.test_get_categories_by_type()))
    test_results.append(("Create Transactions", tester.test_create_transactions()))
    test_results.append(("Get Transactions", tester.test_get_transactions()))
    test_results.append(("Create Budgets", tester.test_create_budgets()))
    test_results.append(("Get Budgets", tester.test_get_budgets()))
    test_results.append(("Budget Overview", tester.test_budget_overview()))
    test_results.append(("Analytics", tester.test_analytics()))
    test_results.append(("Settings", tester.test_settings()))
    test_results.append(("Delete Operations", tester.test_delete_operations()))

    # Print final results
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall API Tests: {tester.tests_passed}/{tester.tests_run} individual calls passed")
    print(f"📈 Test Suites: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 All API tests passed! Backend is working correctly.")
        return 0
    else:
        print("⚠️  Some API tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())