"""Module to process sales data and generate price catalogue."""

import json
import sys
import time
import os
from typing import Dict, List


def load_json_file(filename: str) -> List[Dict]:
    """Loads a JSON file and returns its content as a list of dictionaries."""
    print(f"Loading file: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(
                f"Successfully loaded {filename}, "
                f"{len(data)} records found."
            )
            return data
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading {filename}: {error}")
        return []


def generate_price_catalogue(
    product_list_file: str,
    catalogue_file: str = "priceCatalogue.json"
) -> List[Dict]:
    """Generate a price catalogue from a product list """
    if os.path.exists(catalogue_file):
        return load_json_file(catalogue_file)

    product_list = load_json_file(product_list_file)
    if not product_list:
        print("Error: Product list file is empty or invalid.")
        return []

    catalogue_data = [
        {"title": item["title"], "price": item["price"]}
        for item in product_list
    ]

    with open(catalogue_file, 'w', encoding='utf-8') as file:
        json.dump(catalogue_data, file, indent=4)

    print(
        f"Generated {catalogue_file} with "
        f"{len(catalogue_data)} products."
    )
    return catalogue_data


def compute_total_sales(
    product_catalogue: List[Dict],
    sales_data_list: List[List[Dict]]
) -> Dict[str, float]:
    """The total sales amount for each sales file separately and combined."""
    product_prices = {
        product["title"]: product["price"]
        for product in product_catalogue
    }

    total_sales_per_file = {}
    total_combined_sales = 0.0

    for idx, sales_data in enumerate(sales_data_list, start=1):
        total_sales = 0.0
        for sale in sales_data:
            product_name = sale.get("Product")
            quantity = sale.get("Quantity", 0)

            if product_name in product_prices:
                total_sales += product_prices[product_name] * quantity
            else:
                print(
                    f"Warning: Product '{product_name}' "
                    "not found in catalogue."
                )

        total_sales_per_file[f"Sales File {idx}"] = total_sales
        total_combined_sales += total_sales

    total_sales_per_file["Total Combined Sales"] = total_combined_sales
    return total_sales_per_file


def save_results(
    total_sales_data: Dict[str, float],
    execution_time: float,
    output_file: str = "SalesResults.txt"
) -> None:
    """Saves the computed total sales and execution time to a file."""
    result_text = "\n".join(
        [f"{key}: ${value:.2f}" for key, value in total_sales_data.items()]
    )

    result_text += (
        f"\nExecution Time: {execution_time:.4f} seconds"
    )
    print(result_text)

    with open(output_file, "w", encoding='utf-8') as file:
        file.write(result_text)


def main():
    """Main function to execute the program."""
    if len(sys.argv) < 3:
        print(
            "Usage: python computeSales.py productList.json salesRecord.json "
            "[salesRecord2.json salesRecord3.json ...]"
        )
        sys.exit(1)

    product_list_file = sys.argv[1]
    sales_files = sys.argv[2:]

    start_time = time.time()

    product_catalogue = generate_price_catalogue(product_list_file)
    if not product_catalogue:
        print("Error: Product catalogue could not be loaded correctly.")
        sys.exit(1)

    sales_data_list = [
        load_json_file(sales_file)
        for sales_file in sales_files
    ]
    for idx, sales_data in enumerate(sales_data_list, start=1):
        if not sales_data:
            print(
                f"Error: Sales file {sales_files[idx-1]} "
                "could not be loaded correctly."
            )
            sys.exit(1)

    total_sales_data = compute_total_sales(product_catalogue, sales_data_list)
    execution_time = time.time() - start_time

    save_results(total_sales_data, execution_time)


if __name__ == "__main__":
    main()
