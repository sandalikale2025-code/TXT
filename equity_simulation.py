import os
from collections import defaultdict
from tabulate import tabulate

class Company:
    def __init__(self, id, name, base_price, metric1, metric2):
        self.id = id
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.metric1 = metric1
        self.metric2 = metric2
    
    def apply_scenario_effect(self, multiplier):
        self.current_price = round(self.current_price * multiplier, 2)

class Player:
    def __init__(self, name):
        self.name = name
        self.capital = 100
        self.holdings = defaultdict(int)
    
    def buy_shares(self, company, quantity):
        cost = quantity * company.current_price
        if cost <= self.capital:
            self.capital -= cost
            self.holdings[company.id] += quantity
            return True, f"✓ Bought {quantity} shares of {company.name} for ₹{cost}"
        else:
            return False, f"✗ Not enough capital! Need ₹{cost}, have ₹{self.capital}"
    
    def sell_shares(self, company, quantity):
        if self.holdings[company.id] >= quantity:
            proceeds = quantity * company.current_price
            self.capital += proceeds
            self.holdings[company.id] -= quantity
            return True, f"✓ Sold {quantity} shares of {company.name} for ₹{proceeds}"
        else:
            return False, f"✗ You only own {self.holdings[company.id]} shares of {company.name}"
    
    def get_portfolio_value(self, companies):
        holdings_value = sum(self.holdings[c.id] * c.current_price for c in companies)
        return self.capital + holdings_value
    
    def get_return(self, companies):
        return self.get_portfolio_value(companies) - 100

class SectorShowdown:
    def __init__(self):
        self.companies = [
            Company(1, "TechCorp", 50, "Profit growth: 15%", "Market share: 22%"),
            Company(2, "AIInnovate", 60, "Profit growth: 45%", "Market share: 8%"),
            Company(3, "CloudServe", 40, "Profit growth: 25%", "Market share: 15%")
        ]
        
        self.scenarios = [
            {
                "name": "🔴 New Competitor Enters Market",
                "description": "A major tech competitor launches AI services platform",
                "effects": {1: 0.95, 2: 0.92, 3: 0.98}
            },
            {
                "name": "🟢 Sector Grows 20%",
                "description": "AI adoption accelerates; enterprise spending increases",
                "effects": {1: 1.18, 2: 1.25, 3: 1.15}
            },
            {
                "name": "🟡 Regulatory Changes",
                "description": "New data privacy laws affect the sector differently",
                "effects": {1: 1.08, 2: 0.90, 3: 1.12}
            }
        ]
        
        self.players = {}
        self.current_round = 0
        self.game_active = False
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print("=" * 80)
        print("🎮 SECTOR SHOWDOWN - IT & AI Services Investment Game".center(80))
        print("=" * 80)
        print()
    
    def display_game_status(self):
        if self.current_round == 0:
            status = "Round 0: Setup - Click 'Start Game' to begin"
        elif self.current_round == 1:
            status = "Round 1: Initial Investment - Buy your first shares!"
        else:
            scenario_num = self.current_round - 1
            if scenario_num <= len(self.scenarios):
                status = f"Scenario {scenario_num}: {self.scenarios[scenario_num-1]['name']}"
            else:
                status = f"Round {self.current_round}: Game Complete"
        
        print(f"📊 {status}")
        print()
    
    def display_companies(self):
        print("COMPANIES & SHARE PRICES".center(80))
        print("-" * 80)
        
        for company in self.companies:
            print(f"\n{company.name} (ID: {company.id})")
            print(f"  Current Price: ₹{company.current_price}")
            print(f"  {company.metric1}")
            print(f"  {company.metric2}")
        
        print()
    
    def display_player_portfolio(self, player_name):
        if player_name not in self.players:
            print(f"Player '{player_name}' not found.")
            return
        
        player = self.players[player_name]
        print(f"\n{'Portfolio: ' + player_name}".center(80))
        print("-" * 80)
        print(f"Cash Balance: ₹{round(player.capital, 2)}")
        print(f"\nHoldings:")
        
        portfolio_data = []
        for company in self.companies:
            qty = player.holdings[company.id]
            if qty > 0:
                value = qty * company.current_price
                portfolio_data.append([company.name, qty, f"₹{company.current_price}", f"₹{round(value, 2)}"])
        
        if portfolio_data:
            print(tabulate(portfolio_data, headers=["Company", "Shares", "Price/Share", "Total Value"], tablefmt="grid"))
        else:
            print("No holdings yet")
        
        portfolio_value = player.get_portfolio_value(self.companies)
        returns = player.get_return(self.companies)
        
        print(f"\nTotal Portfolio Value: ₹{round(portfolio_value, 2)}")
        print(f"Return: ₹{round(returns, 2)} ({round((returns/100)*100, 1)}%)")
        print()
    
    def display_leaderboard(self):
        print("\nLEADERBOARD".center(80))
        print("-" * 80)
        
        rankings = []
        for player_name, player in self.players.items():
            portfolio_value = player.get_portfolio_value(self.companies)
            returns = player.get_return(self.companies)
            rankings.append([player_name, f"₹{round(portfolio_value, 2)}", f"₹{round(returns, 2)}", f"{round((returns/100)*100, 1)}%"])
        
        rankings.sort(key=lambda x: float(x[1].replace('₹', '')), reverse=True)
        
        leaderboard_data = []
        for rank, row in enumerate(rankings, 1):
            leaderboard_data.append([rank] + row)
        
        print(tabulate(leaderboard_data, headers=["Rank", "Player", "Portfolio Value", "Return", "Return %"], tablefmt="grid"))
        print()
    
    def display_menu(self):
        print("\nMAIN MENU".center(80))
        print("-" * 80)
        print("1. Start Game")
        print("2. Add/Switch Player")
        print("3. Buy Shares")
        print("4. Sell Shares")
        print("5. View Portfolio")
        print("6. View Leaderboard")
        print("7. Trigger Scenario 1")
        print("8. Trigger Scenario 2")
        print("9. Trigger Scenario 3")
        print("10. Reset Game")
        print("0. Exit")
        print()
    
    def start_game(self):
        self.game_active = True
        self.current_round = 1
        print("✓ Game started! Players can now buy shares.\n")
    
    def add_player(self):
        player_name = input("Enter player name: ").strip()
        if player_name:
            if player_name not in self.players:
                self.players[player_name] = Player(player_name)
                print(f"✓ Player '{player_name}' added with ₹100 capital.\n")
            else:
                print(f"✓ Switched to player '{player_name}'.\n")
            return player_name
        return None
    
    def player_buy(self, player_name):
        if player_name not in self.players:
            print("Player not found. Add a player first.\n")
            return
        
        player = self.players[player_name]
        print("\nAvailable companies:")
        for company in self.companies:
            print(f"  {company.id}. {company.name} - ₹{company.current_price}/share")
        
        try:
            company_id = int(input("\nEnter company ID: "))
            quantity = int(input("Enter quantity: "))
            
            company = next((c for c in self.companies if c.id == company_id), None)
            if company:
                success, message = player.buy_shares(company, quantity)
                print(f"\n{message}\n")
            else:
                print("Invalid company ID.\n")
        except ValueError:
            print("Invalid input. Please enter numbers.\n")
    
    def player_sell(self, player_name):
        if player_name not in self.players:
            print("Player not found. Add a player first.\n")
            return
        
        player = self.players[player_name]
        print("\nYour holdings:")
        for company in self.companies:
            qty = player.holdings[company.id]
            if qty > 0:
                print(f"  {company.id}. {company.name} - {qty} shares @ ₹{company.current_price}/share")
        
        try:
            company_id = int(input("\nEnter company ID to sell: "))
            quantity = int(input("Enter quantity to sell: "))
            
            company = next((c for c in self.companies if c.id == company_id), None)
            if company:
                success, message = player.sell_shares(company, quantity)
                print(f"\n{message}\n")
            else:
                print("Invalid company ID.\n")
        except ValueError:
            print("Invalid input. Please enter numbers.\n")
    
    def trigger_scenario(self, scenario_num):
        if scenario_num < 1 or scenario_num > len(self.scenarios):
            print("Invalid scenario number.\n")
            return
        
        scenario = self.scenarios[scenario_num - 1]
        
        print(f"\n{'SCENARIO ' + str(scenario_num) + ': ' + scenario['name']}".center(80))
        print("-" * 80)
        print(f"Description: {scenario['description']}\n")
        
        print("Price changes:")
        for company in self.companies:
            old_price = company.current_price
            multiplier = scenario['effects'][company.id]
            company.apply_scenario_effect(multiplier)
            change = company.current_price - old_price
            change_pct = round((change / old_price) * 100, 1)
            arrow = "📈" if change >= 0 else "📉"
            print(f"  {company.name}: ₹{old_price} → ₹{company.current_price} ({arrow} {change_pct:+.1f}%)")
        
        self.current_round = scenario_num + 1
        print()
    
    def reset_game(self):
        for company in self.companies:
            company.current_price = company.base_price
        
        self.players = {}
        self.current_round = 0
        self.game_active = False
        print("✓ Game reset.\n")
    
    def run(self):
        current_player = None
        
        while True:
            self.clear_screen()
            self.display_header()
            self.display_game_status()
            self.display_companies()
            
            if self.players:
                self.display_leaderboard()
            
            self.display_menu()
            
            choice = input("Enter your choice (0-10): ").strip()
            
            if choice == "0":
                print("Thanks for playing!")
                break
            elif choice == "1":
                self.start_game()
                input("Press Enter to continue...")
            elif choice == "2":
                current_player = self.add_player()
                input("Press Enter to continue...")
            elif choice == "3":
                if current_player:
                    self.player_buy(current_player)
                else:
                    print("Select a player first (Option 2).\n")
                input("Press Enter to continue...")
            elif choice == "4":
                if current_player:
                    self.player_sell(current_player)
                else:
                    print("Select a player first (Option 2).\n")
                input("Press Enter to continue...")
            elif choice == "5":
                if current_player:
                    self.display_player_portfolio(current_player)
                else:
                    print("Select a player first (Option 2).\n")
                input("Press Enter to continue...")
            elif choice == "6":
                self.display_leaderboard()
                input("Press Enter to continue...")
            elif choice == "7":
                self.trigger_scenario(1)
                input("Press Enter to continue...")
            elif choice == "8":
                self.trigger_scenario(2)
                input("Press Enter to continue...")
            elif choice == "9":
                self.trigger_scenario(3)
                input("Press Enter to continue...")
            elif choice == "10":
                self.reset_game()
                input("Press Enter to continue...")

if __name__ == "__main__":
    game = SectorShowdown()
    game.run()
