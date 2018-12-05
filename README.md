# eBay prices parser
A small project to automatize the retrival of best prices for several items on eBay.

This is specifically intended for a list of books, but can be easily expanded.

The URL is tailored to find italian book, in "buy now" auction format.
It will be expanded in the future to automatically add the required flags to the URL in a dynamic way.

This script is intended to work with `python3`.

It takes a `csv` file as input.
The file must contain the following fields: `Author,Title,Year,Publisher,ISBN`.

The file is read as a `pandas` dataframe, hence it can be easily expanded.

The output is a `csv` file identical to the original, but with addiotional fields: `price` and `Url`.

The `price` containes the best price, the `Url` contains the search results url one should navigate to to perform the purchase.

## Usage
Simply call `$ python ebay_from_ISBN.py`. The input file is hardcoded, for now.


