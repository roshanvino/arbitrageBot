import requests
import json
import pandas as pd
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_odds_data(api_key: str, sport_key: str, region: str, markets: str) -> List[Dict]:
    """
    Fetch odds data from the Odds API.

    :param api_key: API key for authentication.
    :param sport_key: Sport key (e.g., 'soccer_epl' for English Premier League).
    :param region: Region for the odds (e.g., 'uk').
    :param markets: Markets to fetch (e.g., 'h2h').
    :return: List of games with odds data.
    """
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/'
    params = {
        'apiKey': api_key,
        'regions': region,
        'markets': markets
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        odds_data = response.json()
        return odds_data
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP Request failed: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        raise


def build_dataframe(odds_data: List[Dict]) -> pd.DataFrame:
    """
    Build a DataFrame from the odds data.

    :param odds_data: List of games with odds data.
    :return: Pandas DataFrame containing the odds information.
    """
    rows_list = []

    for game in odds_data:
        bookmakers = game.get('bookmakers', [])
        for bookmaker in bookmakers:
            markets = bookmaker.get('markets', [])
            for market_ in markets:
                outcomes = market_.get('outcomes', [])
                for outcome in outcomes:
                    row = {
                        'game_id': game.get('id'),
                        'sport_key': game.get('sport_key'),
                        'sport_title': game.get('sport_title'),
                        'home_team': game.get('home_team'),
                        'away_team': game.get('away_team'),
                        'commence_time': game.get('commence_time'),
                        'bookmaker_key': bookmaker.get('key'),
                        'bookmaker_title': bookmaker.get('title'),
                        'bookmaker_last_update': bookmaker.get('last_update'),
                        'market_key': market_.get('key'),
                        'market_last_update': market_.get('last_update'),
                        'outcome_name': outcome.get('name'),
                        'outcome_price': outcome.get('price')
                    }
                    rows_list.append(row)

    df = pd.DataFrame(rows_list)
    return df


def remove_betting_exchanges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove betting exchanges from the DataFrame.

    :param df: Original DataFrame.
    :return: DataFrame without betting exchanges.
    """
    exchanges = ['betfair_ex_uk', 'betfair_ex_eu', 'matchbook']
    df = df[~df['bookmaker_key'].isin(exchanges)]
    return df


def get_highest_odds(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the highest odds for each game and outcome.

    :param df: DataFrame containing odds data.
    :return: DataFrame with the highest odds for each game and outcome.
    """
    idx = df.groupby(['game_id', 'outcome_name'])['outcome_price'].idxmax()
    df_highest = df.loc[idx].reset_index(drop=True)
    return df_highest


def find_arbitrage_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify arbitrage opportunities.

    :param df: DataFrame with the highest odds.
    :return: DataFrame containing arbitrage opportunities.
    """
    df['implied_probability'] = 1 / df['outcome_price']
    df['sum_implied_prob'] = df.groupby('game_id')['implied_probability'].transform('sum')
    arbitrage_df = df[df['sum_implied_prob'] < 1].copy()
    return arbitrage_df


def calculate_stakes(df: pd.DataFrame, total_stake: float) -> pd.DataFrame:
    """
    Calculate stakes and ROI for arbitrage opportunities.

    :param df: DataFrame containing arbitrage opportunities.
    :param total_stake: Total amount to stake.
    :return: DataFrame with calculated stakes and ROI.
    """
    df['stake'] = (total_stake / df['sum_implied_prob']) * df['implied_probability']
    df['roi'] = 1 - df['sum_implied_prob']
    return df


def display_arbitrage_opportunities(df: pd.DataFrame):
    """
    Display arbitrage opportunities in a neat, separated format.

    :param df: DataFrame containing arbitrage opportunities.
    """
    grouped = df.groupby('game_id')
    for game_id, group in grouped:
        print("\n" + "=" * 50)
        print(f"Game ID: {game_id}")
        print(f"{group.iloc[0]['home_team']} vs {group.iloc[0]['away_team']}")
        print(f"Commence Time: {group.iloc[0]['commence_time']}")
        print("\nArbitrage Opportunities:")
        for _, row in group.iterrows():
            print(f" - Outcome: {row['outcome_name']}")
            print(f"   Bookmaker: {row['bookmaker_title']}")
            print(f"   Odds: {row['outcome_price']:.2f}")
            print(f"   Stake: £{row['stake']:.2f}")
        roi = group.iloc[0]['roi']
        print(f"\nEstimated ROI: {roi:.2%}")
        print("=" * 50)


def main():
    # Replace with your API key
    api_key = "3534c6a066f5fe4b5e7a6ce4b575c04e"
    region = "uk"  # Focus on UK market
    markets = "h2h"  # Full-time result market
    sport_key = "soccer_epl"  # English Premier League

    try:
        odds_data = fetch_odds_data(api_key, sport_key, region, markets)
    except Exception as e:
        logging.error("Failed to fetch odds data.")
        return

    df = build_dataframe(odds_data)
    df = remove_betting_exchanges(df)
    df_highest_odds = get_highest_odds(df)
    df_arbitrage = find_arbitrage_opportunities(df_highest_odds)

    if df_arbitrage.empty:
        logging.info("No arbitrage opportunities found.")
        return

    total_stake = 1000
    df_arbitrage = calculate_stakes(df_arbitrage, total_stake)

    # Display the arbitrage opportunities
    display_arbitrage_opportunities(df_arbitrage)


if __name__ == "__main__":
    main()
