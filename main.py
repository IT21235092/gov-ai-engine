from app.scrapers.gazette_scraper import scrape_gazette
from app.pipelines.structure_and_embed import process_notices

if __name__ == "__main__":
    scrape_gazette()
    process_notices()