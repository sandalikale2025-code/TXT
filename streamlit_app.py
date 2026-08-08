import streamlit as st
import json
import os
from datetime import datetime

# Configure Streamlit
st.set_page_config(page_title="Sector Showdown", layout="wide", initial_sidebar_state="expanded")

# File for persistent storage
DATA_FILE = "game_data.json"

# Game configuration
COMPANIES = {
    1: {"name": "TechCorp", "base_price": 50, "metric1": "Profit growth: 15%", "metric2": "Market share: 22%"},
    2: {"name": "AIInnovate", "base_price": 60, "metric1": "Profit growth: 45%", "metric2": "Market share: 8%"},
    3: {"name": "CloudServe", "base_price": 40, "metric1": "Profit growth: 25%", "metric2": "Market share: 15%"}
}

SCENARIOS = [
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

# Initialize session state
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "active": False,
        "round": 0,
        "companies": {k: {"price": v["base_price"], **v} for k, v in COMPANIES.items()},
        "players": {},
        "last_scenario": None
    }

if "current_player" not in st.session_state:
    st.session_state.current_player = None

# File I/O functions
def load_game_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_game_state(state):
    with open(DATA_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_game():
    loaded = load_game_state()
    if loaded:
        st.session_state.game_state = loaded

def save_game():
    save_game_state(st.session_state.game_state)

# Load game state on startup
load_game()

# UI Functions
def display_header():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🎮 Sector Showdown", unsafe_allow_html=True)
        st.markdown("### IT & AI Services Investment Game", unsafe_allow_html=True)
    
    # Game status
    state = st.session_state.game_state
    if state["active"]:
        if state["round"] == 1:
            st.info("📊 Round 1: Initial Investment - Buy your first shares!")
        elif state["round"] > 1 and state["round"] <= len(SCENARIOS) + 1:
            scenario_idx = state["round"] - 2
            if scenario_idx < len(SCENARIOS):
                st.warning(f"📊 Scenario {scenario_idx + 1}: {SCENARIOS[scenario_idx]['name']}")
        else:
            st.success("✅ Game Complete - Check the leaderboard!")
    else:
        st.error("⏸️ Game not started yet")

def display_companies():
    st.subheader("Companies & Current Prices")
    
    state = st.session_state.game_state
    companies = state["companies"]
    
    cols = st.columns(3)
    for idx, (company_id, company) in enumerate(companies.items()):
        with cols[idx]:
            st.markdown(f"""
            ### {company['name']}
            **Current Price:** ₹{company['price']}
            
            {company['metric1']}  
            {company['metric2']}
            """)

def display_portfolio():
    st.subheader(f"📈 {st.session_state.current_player}'s Portfolio")
    
    state = st.session_state.game_state
    companies = state["companies"]
    
    if st.session_state.current_player not in state["players"]:
        st.info("No holdings yet. Start buying!")
        return
    
    player = state["players"][st.session_state.current_player]
    
    # Holdings
    holdings_data = []
    for company_id, qty in player["holdings"].items():
        if qty > 0:
            company = companies[company_id]
            value = qty * company["price"]
            holdings_data.append({
                "Company": company["name"],
                "Shares": qty,
                "Price/Share": f"₹{company['price']}",
                "Total Value": f"₹{value:.2f}"
            })
    
    if holdings_data:
        st.dataframe(holdings_data, use_container_width=True, hide_index=True)
    else:
        st.info("No holdings yet")
    
    # Summary
    portfolio_value = player["capital"] + sum(player["holdings"].get(cid, 0) * companies[cid]["price"] for cid in companies)
    returns = portfolio_value - 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cash", f"₹{player['capital']:.2f}")
    with col2:
        st.metric("Portfolio Value", f"₹{portfolio_value:.2f}")
    with col3:
        st.metric("Return", f"₹{returns:.2f}", f"{(returns/100)*100:.1f}%")

def display_leaderboard():
    st.subheader("🏆 Leaderboard")
    
    state = st.session_state.game_state
    companies = state["companies"]
    
    if not state["players"]:
        st.info("No players yet")
        return
    
    rankings = []
    for player_name, player_data in state["players"].items():
        portfolio_value = player_data["capital"] + sum(player_data["holdings"].get(cid, 0) * companies[cid]["price"] for cid in companies)
        returns = portfolio_value - 100
        rankings.append({
            "Player": player_name,
            "Portfolio Value": f"₹{portfolio_value:.2f}",
            "Return": f"₹{returns:.2f}",
            "Return %": f"{(returns/100)*100:.1f}%"
        })
    
    rankings.sort(key=lambda x: float(x["Portfolio Value"].replace("₹", "")), reverse=True)
    
    # Add rank
    for idx, row in enumerate(rankings, 1):
        row["Rank"] = idx
    
    rankings = [{k: v for k, v in row.items() if k == "Rank"} | {k: v for k, v in row.items() if k != "Rank"} for row in rankings]
    
    st.dataframe(rankings, use_container_width=True, hide_index=True)

# Main UI
display_header()

# Sidebar for player management
with st.sidebar:
    st.markdown("### Player Management")
    
    player_name = st.text_input("Enter your name:", placeholder="e.g., Sandali")
    
    if player_name and st.button("Join Game"):
        state = st.session_state.game_state
        if player_name not in state["players"]:
            state["players"][player_name] = {
                "capital": 100,
                "holdings": {1: 0, 2: 0, 3: 0}
            }
            save_game()
        st.session_state.current_player = player_name
        st.success(f"✓ Joined as {player_name}")
        st.rerun()
    
    if st.session_state.current_player:
        st.markdown(f"**Current Player:** {st.session_state.current_player}")
        
        if st.button("Logout"):
            st.session_state.current_player = None
            st.rerun()
    
    st.divider()
    
    # Admin panel
    st.markdown("### Admin Controls")
    admin_password = st.text_input("Admin Password:", type="password")
    
    if admin_password == "IC2024":
        st.success("✓ Admin access granted")
        
        state = st.session_state.game_state
        
        if st.button("🎮 Start Game"):
            state["active"] = True
            state["round"] = 1
            st.success("Game started!")
            save_game()
            st.rerun()
        
        if state["active"]:
            st.markdown("#### Trigger Scenarios")
            for idx, scenario in enumerate(SCENARIOS, 1):
                if st.button(f"Scenario {idx}: {scenario['name']}"):
                    # Apply scenario effects
                    for company_id, multiplier in scenario['effects'].items():
                        state["companies"][company_id]["price"] = round(state["companies"][company_id]["price"] * multiplier, 2)
                    
                    state["round"] = idx + 1
                    state["last_scenario"] = scenario["name"]
                    save_game()
                    st.success(f"Scenario {idx} triggered! Prices updated.")
                    st.rerun()
        
        if st.button("🔄 Reset Game"):
            st.session_state.game_state = {
                "active": False,
                "round": 0,
                "companies": {k: {"price": v["base_price"], **v} for k, v in COMPANIES.items()},
                "players": {},
                "last_scenario": None
            }
            st.session_state.current_player = None
            save_game()
            st.success("Game reset!")
            st.rerun()

# Main content area
tab1, tab2, tab3 = st.tabs(["📊 Market", "📈 My Portfolio", "🏆 Leaderboard"])

with tab1:
    display_companies()
    
    if st.session_state.current_player and st.session_state.game_state["active"]:
        st.divider()
        st.subheader("Buy & Sell Shares")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            company_id = st.selectbox("Select Company", list(COMPANIES.keys()), format_func=lambda x: COMPANIES[x]["name"])
        
        with col2:
            qty = st.number_input("Quantity", min_value=1, value=1)
        
        with col3:
            action = st.selectbox("Action", ["Buy", "Sell"])
        
        state = st.session_state.game_state
        company = state["companies"][company_id]
        player = state["players"][st.session_state.current_player]
        
        if action == "Buy":
            cost = qty * company["price"]
            if st.button(f"💰 Buy {qty} shares for ₹{cost:.2f}"):
                if cost <= player["capital"]:
                    player["capital"] -= cost
                    player["holdings"][company_id] += qty
                    save_game()
                    st.success(f"✓ Bought {qty} shares of {company['name']}!")
                    st.rerun()
                else:
                    st.error(f"Not enough capital! Need ₹{cost}, have ₹{player['capital']}")
        
        else:  # Sell
            if st.button(f"📉 Sell {qty} shares"):
                if player["holdings"][company_id] >= qty:
                    proceeds = qty * company["price"]
                    player["capital"] += proceeds
                    player["holdings"][company_id] -= qty
                    save_game()
                    st.success(f"✓ Sold {qty} shares of {company['name']} for ₹{proceeds:.2f}!")
                    st.rerun()
                else:
                    st.error(f"You only own {player['holdings'][company_id]} shares")

with tab2:
    if st.session_state.current_player:
        display_portfolio()
    else:
        st.info("Join the game first (enter your name in the sidebar)")

with tab3:
    display_leaderboard()

# Footer
st.divider()
st.markdown("""
### How to Play
1. **Join**: Enter your name in the sidebar and click "Join Game"
2. **Buy & Sell**: Go to the Market tab, select a company, enter quantity, and buy/sell
3. **React to Scenarios**: When the admin triggers scenarios, prices change - rebalance your portfolio!
4. **Win**: Highest portfolio value at the end wins!

**Strategy Tip:** Compare companies in the same sector. How do they stack up against each other?
""")
