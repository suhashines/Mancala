import matplotlib.pyplot as plt
import pandas as pd


gameframe = pd.read_csv('analysis.csv')

print(gameframe.head(50))

def calculate_performance(player, df):
    heuristics = df[player].unique()  
    performance = {}
    
    for heuristic in heuristics:
        total_games = len(df[df[player] == heuristic])
        wins = len(df[(df[player] == heuristic) & (df['result'] == player)])
        draws = len(df[(df[player] == heuristic) & (df['result'] == 'draw')])
        losses = total_games - wins - draws
        
        performance[heuristic] = [wins / total_games * 100, losses / total_games * 100, draws / total_games * 100]
    
   
    total_games = len(df)
    print(f"total games:{total_games}")
    total_wins = len(df[df['result'] == player])
    print(f"total wins:{total_wins}")
    total_draws = len(df[df['result'] == 'draw'])
    print(f"total draws:{total_draws}")
    total_losses = total_games - total_wins - total_draws
    print(f"total losses:{total_losses}")

   
    if total_games > 0:
        performance['Overall'] = [
            total_wins / total_games * 100,
            total_losses / total_games * 100,
            total_draws / total_games * 100
        ]
    else:
        performance['Overall'] = [0, 0, 0]  # If no games were played, set percentages to 0
    
    return performance


def plot_pie_charts(player, df):

    performance = calculate_performance(player, df)

    print(f"performance of {player}: {performance}")

    heuristics = list(performance.keys())
    
   
    num_heuristics = len(heuristics)

    
    fig, axs = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle(f'{player} Performance by Heuristic', fontsize=16)

    axs = axs.flatten()

   
    colors = ['#4CAF50', '#F44336', '#FFC107']  # Green: Wins, Red: Losses, Yellow: Draws
    labels = ['Wins', 'Losses', 'Draws']
    
   
    for idx, heuristic in enumerate(heuristics):
        axs[idx].pie(performance[heuristic], labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        axs[idx].set_title(f'{heuristic}')
    
 
    for idx in range(num_heuristics, 6):
        fig.delaxes(axs[idx]) 
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

# Plotting for Player 1
plot_pie_charts('P1', gameframe)

# Plotting for Player 2
plot_pie_charts('P2', gameframe)
