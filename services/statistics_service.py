import pytz
from models.statistics import Statistics
from repositories.statistics_repository import StatisticsRepository
from utils.custom_driver import CustomDriver
from utils.custom_soup import CustomSoup
from datetime import datetime, timedelta

from io import StringIO
import pandas as pd
class StatisticsService:
    statistics_repository: StatisticsRepository

    def __init__(self):
        self.statistics_repository = StatisticsRepository()

    def get_stats(self):
        stats = Statistics(
            id=-1,
            name="AI Preparedness Index",
            url="https://www.imf.org/external/datamapper/AI_PI@AIPI/ADVEC/EME/LIC",
            stats={},
            updateAt=None,
        )
        driver: CustomDriver = CustomDriver()
        
        updated_date: str | None = self.statistics_repository.get_updated_date(stats.name)
        
        if updated_date:
            # Parse the date string into a datetime object
            updated_datetime = datetime.strptime(updated_date, "%Y-%m-%d %H:%M:%S")
            # Check if the date is within the last 3 days
            min_date = timedelta(days=3)
            if updated_datetime.replace(tzinfo=pytz.UTC) > datetime.now().replace(tzinfo=pytz.UTC) - min_date:
                return

        driver.get(stats.url)

        html: str = driver.get_html()

        soup: CustomSoup = CustomSoup(html=html)

        download_link: str | None = soup.select_url(
            base_url="https://www.imf.org/",
            css_selector='button.dm-share-button[data-type="excel"]',
        )
        if download_link:
            excel_file = driver.download_file(download_link)

            # Read the Excel file into a DataFrame
            df = pd.read_excel(StringIO(excel_file))

            # Convert DataFrame to dictionary
            stats_dict = df.to_dict(orient="records")

            # Update the stats with the dictionary data
            stats.stats = {"data": stats_dict}
