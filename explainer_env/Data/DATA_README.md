# Dataset
posts_data_unique.csv - the cleaned version of the webscraped content of the posts, removed duplicates, main dataset
links_data.csv - the webscraped content of the onion links that were responding
links_to_sites.csv - contains known links and aliases to specific marketplaces and related sites

# Explaner related data
explainer_posts.csv - a single page from DarkNetMarkets consisting of 20 posts for the purpose of explaining the scrapping process
explainer_posts_unique.csv - The same as above, since there were no diplicates

# Additional files
explainer.ipynb - the Explainer Notebook
DreadScraper.py - the webscraping tool, developed by the authors of the dataset
idf.json - the IDF file for the entire dataset (it takes a while to compute)
U2U.json - the User networkx graph based on the largest connected component of the dataset
U2L.json - the marketplaces networkx graph based on the largest connected component of the dataset