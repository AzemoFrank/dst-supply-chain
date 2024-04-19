import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

class Geocoder:
    def __init__(self, user_agent="geoapiExercises", min_delay_seconds=1):
        self.geolocator = Nominatim(user_agent=user_agent)
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=min_delay_seconds)

    def get_location_by_address(self, address):


        """
            Retrieve geographical coordinates (latitude, longitude) for a given address.

            Parameters:
            - address (str): l'addresse pour obtenir les coordinates.

            Returns:
            - tuple: si l'adresse est trouvé elle returen une tuple (latitude, longitude) ,
             sinon returns (None, None).

             Raises:
             - Exception: afficher une error message dans le consol si le geocoding ehouée.
        """
        try:
            location = self.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            else:
                return (None, None)
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
            return (None, None)

    def add_coordinates(self, df, address_column='Location'):
        """ `df` a un colonne Location` """
        df['Coordinates'] = df[address_column].apply(self.get_location_by_address)
        df[['Latitude', 'Longitude']] = pd.DataFrame(df['Coordinates'].tolist(), index=df.index)
        df.drop(columns=['Coordinates'], inplace=True)  # Clean up if not needed anymore




if __name__ == '__main__':
    df_test = pd.read_csv("entreprises.csv")

    # Create an instance of the Geocoder
    geocoder = Geocoder(user_agent="test_app")

    # Test adding coordinates to the DataFrame
    geocoder.add_coordinates(df_test)
    print(df_test)

    # Test individual address geocoding
    for address in df_test['Location']:
        result = geocoder.get_location_by_address(address)
        print(f"Result for '{address}': {result}")