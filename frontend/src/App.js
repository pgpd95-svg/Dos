import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Separator } from "./components/ui/separator";
import { Trash2, Plus, TrendingUp, TrendingDown, Wallet, Target, Calendar, DollarSign } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [budgetOverview, setBudgetOverview] = useState([]);
  const [settings, setSettings] = useState({ default_currency: 'USD' });
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');
  const [spendingData, setSpendingData] = useState([]);

  // Form states
  const [transactionForm, setTransactionForm] = useState({
    type: 'expense',
    amount: '',
    category_id: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    currency: 'USD'
  });
  
  const [categoryForm, setCategoryForm] = useState({
    name: '',
    color: '#3B82F6',
    type: 'expense'
  });

  const [budgetForm, setBudgetForm] = useState({
    category_id: '',
    amount: '',
    period: 'monthly',
    currency: 'USD'
  });

  const [isTransactionDialogOpen, setIsTransactionDialogOpen] = useState(false);
  const [isCategoryDialogOpen, setIsCategoryDialogOpen] = useState(false);
  const [isBudgetDialogOpen, setIsBudgetDialogOpen] = useState(false);

  // Fetch data functions
  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API}/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchBudgetOverview = async () => {
    try {
      const response = await axios.get(`${API}/budget-overview/${selectedPeriod}`);
      setBudgetOverview(response.data);
    } catch (error) {
      console.error('Error fetching budget overview:', error);
    }
  };

  const fetchSpendingData = async () => {
    try {
      const response = await axios.get(`${API}/analytics/spending-by-category?period=${selectedPeriod}`);
      setSpendingData(response.data);
    } catch (error) {
      console.error('Error fetching spending data:', error);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`);
      setSettings(response.data);
      setTransactionForm(prev => ({ ...prev, currency: response.data.default_currency }));
      setBudgetForm(prev => ({ ...prev, currency: response.data.default_currency }));
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  // Create functions
  const createTransaction = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/transactions`, {
        ...transactionForm,
        amount: parseFloat(transactionForm.amount)
      });
      setTransactionForm({
        type: 'expense',
        amount: '',
        category_id: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        currency: settings.default_currency
      });
      setIsTransactionDialogOpen(false);
      fetchTransactions();
      fetchBudgetOverview();
      fetchSpendingData();
    } catch (error) {
      console.error('Error creating transaction:', error);
    }
  };

  const createCategory = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/categories`, categoryForm);
      setCategoryForm({
        name: '',
        color: '#3B82F6',
        type: 'expense'
      });
      setIsCategoryDialogOpen(false);
      fetchCategories();
    } catch (error) {
      console.error('Error creating category:', error);
    }
  };

  const createBudget = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/budgets`, {
        ...budgetForm,
        amount: parseFloat(budgetForm.amount)
      });
      setBudgetForm({
        category_id: '',
        amount: '',
        period: 'monthly',
        currency: settings.default_currency
      });
      setIsBudgetDialogOpen(false);
      fetchBudgetOverview();
    } catch (error) {
      console.error('Error creating budget:', error);
    }
  };

  const deleteTransaction = async (id) => {
    try {
      await axios.delete(`${API}/transactions/${id}`);
      fetchTransactions();
      fetchBudgetOverview();
      fetchSpendingData();
    } catch (error) {
      console.error('Error deleting transaction:', error);
    }
  };

  const updateCurrency = async (currency) => {
    try {
      await axios.put(`${API}/settings`, { default_currency: currency });
      fetchSettings();
    } catch (error) {
      console.error('Error updating currency:', error);
    }
  };

  // Calculate totals
  const totalIncome = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
  const totalExpenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
  const netAmount = totalIncome - totalExpenses;

  useEffect(() => {
    fetchTransactions();
    fetchCategories();
    fetchSettings();
  }, []);

  useEffect(() => {
    fetchBudgetOverview();
    fetchSpendingData();
  }, [selectedPeriod]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Budget Tracker</h1>
            <p className="text-slate-600">Manage your finances with ease</p>
          </div>
          <div className="flex items-center gap-4">
            <Select value={settings.default_currency} onValueChange={updateCurrency}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="USD">USD</SelectItem>
                <SelectItem value="EUR">EUR</SelectItem>
                <SelectItem value="GBP">GBP</SelectItem>
                <SelectItem value="JPY">JPY</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-green-800">Total Income</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-900">
                {settings.default_currency} {totalIncome.toFixed(2)}
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-red-800">Total Expenses</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-900">
                {settings.default_currency} {totalExpenses.toFixed(2)}
              </div>
            </CardContent>
          </Card>
          
          <Card className={`bg-gradient-to-br ${netAmount >= 0 ? 'from-blue-50 to-blue-100 border-blue-200' : 'from-orange-50 to-orange-100 border-orange-200'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${netAmount >= 0 ? 'text-blue-800' : 'text-orange-800'}`}>Net Amount</CardTitle>
              <Wallet className={`h-4 w-4 ${netAmount >= 0 ? 'text-blue-600' : 'text-orange-600'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${netAmount >= 0 ? 'text-blue-900' : 'text-orange-900'}`}>
                {settings.default_currency} {netAmount.toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Budget Overview */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5" />
                      Budget Overview ({selectedPeriod})
                    </CardTitle>
                    <CardDescription>Track your spending against budgets</CardDescription>
                  </div>
                  <Dialog open={isBudgetDialogOpen} onOpenChange={setIsBudgetDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm">
                        <Plus className="h-4 w-4 mr-1" />
                        Set Budget
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Set Budget</DialogTitle>
                        <DialogDescription>Create a new budget for a category</DialogDescription>
                      </DialogHeader>
                      <form onSubmit={createBudget} className="space-y-4">
                        <div>
                          <Label htmlFor="budget-category">Category</Label>
                          <Select value={budgetForm.category_id} onValueChange={(value) => setBudgetForm({...budgetForm, category_id: value})}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select category" />
                            </SelectTrigger>
                            <SelectContent>
                              {categories.filter(c => c.type === 'expense').map(category => (
                                <SelectItem key={category.id} value={category.id}>{category.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="budget-amount">Budget Amount</Label>
                          <Input
                            id="budget-amount"
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={budgetForm.amount}
                            onChange={(e) => setBudgetForm({...budgetForm, amount: e.target.value})}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="budget-period">Period</Label>
                          <Select value={budgetForm.period} onValueChange={(value) => setBudgetForm({...budgetForm, period: value})}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="weekly">Weekly</SelectItem>
                              <SelectItem value="monthly">Monthly</SelectItem>
                              <SelectItem value="yearly">Yearly</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Button type="submit" className="w-full">Create Budget</Button>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {budgetOverview.map(budget => (
                    <div key={budget.category_id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: budget.category_color }}
                          />
                          <span className="font-medium">{budget.category_name}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-slate-600">
                            {budget.currency} {budget.spent_amount.toFixed(2)} / {budget.budget_amount.toFixed(2)}
                          </div>
                          {budget.is_over_budget && (
                            <Badge variant="destructive" className="text-xs">Over Budget</Badge>
                          )}
                        </div>
                      </div>
                      <Progress 
                        value={Math.min(budget.percentage_used, 100)} 
                        className="h-2"
                      />
                      <div className="flex justify-between text-xs text-slate-500">
                        <span>{budget.percentage_used.toFixed(1)}% used</span>
                        <span>{budget.remaining_amount.toFixed(2)} remaining</span>
                      </div>
                    </div>
                  ))}
                  {budgetOverview.length === 0 && (
                    <div className="text-center text-slate-500 py-8">
                      No budgets set for {selectedPeriod} period
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Spending by Category Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Spending by Category
                </CardTitle>
                <CardDescription>Your top spending categories this {selectedPeriod}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {spendingData.slice(0, 5).map((item, index) => (
                    <div key={item.category_id} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-lg font-bold text-slate-400">#{index + 1}</div>
                        <div 
                          className="w-4 h-4 rounded-full" 
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="font-medium">{item.category_name}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{settings.default_currency} {item.total_spent.toFixed(2)}</div>
                        <div className="text-xs text-slate-500">{item.transaction_count} transactions</div>
                      </div>
                    </div>
                  ))}
                  {spendingData.length === 0 && (
                    <div className="text-center text-slate-500 py-8">
                      No spending data for {selectedPeriod} period
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Quick Add Transaction */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Dialog open={isTransactionDialogOpen} onOpenChange={setIsTransactionDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full" size="lg">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Transaction
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Transaction</DialogTitle>
                      <DialogDescription>Record a new income or expense</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createTransaction} className="space-y-4">
                      <Tabs value={transactionForm.type} onValueChange={(value) => setTransactionForm({...transactionForm, type: value})}>
                        <TabsList className="grid w-full grid-cols-2">
                          <TabsTrigger value="income">Income</TabsTrigger>
                          <TabsTrigger value="expense">Expense</TabsTrigger>
                        </TabsList>
                      </Tabs>
                      
                      <div>
                        <Label htmlFor="amount">Amount</Label>
                        <Input
                          id="amount"
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={transactionForm.amount}
                          onChange={(e) => setTransactionForm({...transactionForm, amount: e.target.value})}
                          required
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="category">Category</Label>
                        <Select value={transactionForm.category_id} onValueChange={(value) => setTransactionForm({...transactionForm, category_id: value})}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select category" />
                          </SelectTrigger>
                          <SelectContent>
                            {categories.filter(c => c.type === transactionForm.type).map(category => (
                              <SelectItem key={category.id} value={category.id}>{category.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="description">Description (optional)</Label>
                        <Input
                          id="description"
                          placeholder="Transaction description"
                          value={transactionForm.description}
                          onChange={(e) => setTransactionForm({...transactionForm, description: e.target.value})}
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="date">Date</Label>
                        <Input
                          id="date"
                          type="date"
                          value={transactionForm.date}
                          onChange={(e) => setTransactionForm({...transactionForm, date: e.target.value})}
                          required
                        />
                      </div>
                      
                      <Button type="submit" className="w-full">Add Transaction</Button>
                    </form>
                  </DialogContent>
                </Dialog>

                <Dialog open={isCategoryDialogOpen} onOpenChange={setIsCategoryDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Category
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Category</DialogTitle>
                      <DialogDescription>Create a new category for your transactions</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createCategory} className="space-y-4">
                      <div>
                        <Label htmlFor="category-name">Category Name</Label>
                        <Input
                          id="category-name"
                          placeholder="Category name"
                          value={categoryForm.name}
                          onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
                          required
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="category-type">Type</Label>
                        <Select value={categoryForm.type} onValueChange={(value) => setCategoryForm({...categoryForm, type: value})}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="income">Income</SelectItem>
                            <SelectItem value="expense">Expense</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="category-color">Color</Label>
                        <Input
                          id="category-color"
                          type="color"
                          value={categoryForm.color}
                          onChange={(e) => setCategoryForm({...categoryForm, color: e.target.value})}
                        />
                      </div>
                      
                      <Button type="submit" className="w-full">Create Category</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>

            {/* Recent Transactions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Recent Transactions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {transactions.slice(0, 10).map(transaction => (
                    <div key={transaction.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={transaction.type === 'income' ? 'default' : 'secondary'}>
                            {transaction.type}
                          </Badge>
                          <span className="font-medium text-sm">{transaction.category_name}</span>
                        </div>
                        <div className="text-xs text-slate-600">
                          {transaction.description && <div>{transaction.description}</div>}
                          <div>{transaction.date}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                          {transaction.type === 'income' ? '+' : '-'}{transaction.currency} {transaction.amount.toFixed(2)}
                        </span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => deleteTransaction(transaction.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  {transactions.length === 0 && (
                    <div className="text-center text-slate-500 py-8">
                      No transactions yet
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;