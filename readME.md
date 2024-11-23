# Arbitrage Betting Bot

## Overview

The Arbitrage Betting Bot is a Python-based tool that identifies profitable arbitrage opportunities in sports betting. By analyzing odds from multiple bookmakers, the bot calculates guaranteed profit scenarios, regardless of the game's outcome.

## Features

- **Live Odds Fetching**: Retrieves real-time sports betting odds from multiple bookmakers via the Odds API.
- **Arbitrage Detection**: Identifies arbitrage opportunities by calculating implied probabilities and finding opportunities where the sum of probabilities is less than 1.
- **Stake Optimization**: Calculates the optimal stake for each outcome to maximize ROI.
- **Multi-Sport Support**: Configurable for different sports and leagues (default is English Premier League).
- **Excludes Betting Exchanges**: Filters out odds from betting exchanges to focus on traditional bookmakers.
- **Customizable Stake**: Allows users to define the total amount to bet.

## Prerequisites

- Python 3.8 or higher
- A valid API key from [The Odds API](https://the-odds-api.com/)
- Libraries listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/arbitrage-betting-bot.git
   cd arbitrage-betting-bot
