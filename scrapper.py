import time
import pandas as pd
import random
import glob
import os
import datetime
import requests  # Importe la bibliothèque requests, utilisée pour envoyer des requêtes HTTP en Python.
from bs4 import BeautifulSoup as ps # Importe la classe BeautifulSoup de la bibliothèque bs4 et la renomme ps pour l'analyse du contenu HTML.
import multiprocessing


def unify_csv_files(csv_directory, output_file):
  """
  This function unifies multiple CSV files from a directory into a single CSV file.

  Args:
      csv_directory (str): Path to the directory containing the CSV files.
      output_file (str): Path to the output file where the unified data will be saved.
  """
  all_files = glob.glob(f"{csv_directory}/*.csv")  # Find all CSV files in the directory

  # Check if any CSV files were found
  if not all_files:
      print(f"No CSV files found in directory: {csv_directory}")
      return

  # Read the first CSV file
  df = pd.read_csv(all_files[0])

  # Read subsequent CSV files and append them to the dataframe
  for filename in all_files[1:]:
      df = pd.concat([df, pd.read_csv(filename)], ignore_index=True)

  # Save the unified dataframe to a new CSV file
  df.to_csv(output_file, index=False)

  print(f"CSV files unified and saved to: {output_file}")


def create_dir_with_timestamp(base_dir):
  """
  This function creates a new directory with a timestamp appended to its name.

  Args:
      base_dir (str): The base directory path where the new directory will be created.

  Returns:
      str: The path to the newly created directory.
  """
  now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Get current date and time
  new_dir_name = os.path.join(base_dir, now)  # Combine base dir and timestamp

  # Check if directory already exists (optional)
  if os.path.exists(new_dir_name):
      print(f"Directory with timestamp '{now}' already exists. Creating one with a suffix.")
      i = 1
      while os.path.exists(f"{new_dir_name}_{i}"):
          i += 1
      new_dir_name = f"{new_dir_name}_{i}"

  # Create the directory
  os.makedirs(new_dir_name)

  return new_dir_name

  
def scrapper_les_entreprises(base_dir):
    #Définition de l'URL cible
    url_Cat_Transp_Logistique="https://fr.trustpilot.com/categories/business_services?subcategories=shipping_logistics"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    Page_HtMl=requests.get(url_Cat_Transp_Logistique, headers)

    Soup=ps(Page_HtMl.content,'lxml')

    #  listes pour stocker les informations
    entreprises = []
    locations = []
    trust_scores = []
    nombre_avis = []
    services_proposes = []
    entreprises_urls = []

    # pages à parcourir
    nombre_de_pages = 11 

    # parcourur le nombre de pages
    for page in range(1, nombre_de_pages + 1):
        # Construction de l'URL ppour chaque page
        url = f"https://fr.trustpilot.com/categories/business_services?page={page}&subcategories=shipping_logistics"
        
        # Requête HTTP pour récupere la page html
        response = requests.get(url, headers)
        # beautifulesoup pour parcer avec le parceaus lxml
        
        soup = ps(response.content, 'lxml')
        
        # iodentifier les information et les extraire de la page courante
        info_entreprises = soup.find_all('div', class_="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2")
        
        for entreprise in info_entreprises:
            # pour chque information , on l extraire de ca baliser et les sotcker dans la table correspondants
            # Nom_entrprise
            nom = entreprise.find('p', class_='styles_displayName__GOhL2').text if entreprise.find('p', class_='styles_displayName__GOhL2') else 'Non'
            entreprises.append(nom)
            # Score_entrprise
            score = entreprise.find('span', class_='styles_trustScore__8emxJ')
            trust_scores.append(score.text.replace('TrustScore', '').strip().replace(',', '.') if score else '0')
            # Nb avise_entrprise
            avis_obj = entreprise.find('p', class_='styles_ratingText__yQ5S7')
            avis_text = avis_obj.text if avis_obj is not None else ""
            parts = avis_text.split('|')
            nombre_avis.append(''.join(filter(str.isdigit, parts[1])) if len(parts) > 1 else '0')
            # lieu_entrprise
            loc = entreprise.find('span', class_='styles_location__ILZb0')
            locations.append(loc.text if loc else 'Non ')
            # services proposé_entrprise
            services_elems = entreprise.find_all('span', class_='typography_body-s__aY15Q')
            services_proposes.append([service.text for service in services_elems] if services_elems else ['Non'])
            # lieu_entrprise
            url_entreprise = entreprise.find('a')['href']
            entreprises_urls.append(f"https://fr.trustpilot.com{url_entreprise}" if url_entreprise else 'Non')

    # Création d'un DataFrame 
    df_entreprises = pd.DataFrame({
        'Entreprise': entreprises,
        'Url': entreprises_urls,
        'Location': locations,
        'TrustScore': trust_scores,
        'NombreAvis': nombre_avis,
        'ServicesProposes': services_proposes
    })

    df_entreprises = df_entreprises.astype({
        'Entreprise': 'object',
        'Url': 'object',
        'Location': 'object',
        'TrustScore': 'float64',
        'NombreAvis': 'int64',
        'ServicesProposes': 'object'
    })

    print(df_entreprises.head())
    print(df_entreprises.info())

    # stocker dans ficher csv
    df_entreprises.to_csv(f'{base_dir}/entreprises.csv', index=False)

    del(entreprises)
    del(locations)
    del(trust_scores)
    del(nombre_avis)
    del(services_proposes)
    del(entreprises_urls)
    del(df_entreprises)
    time.sleep(20)
    

def scrapper_les_avis_par_pages(page_obj):
    
    random_num = random.randint(5, 15)
    facteur = page_obj['page']//100 + 1
    temps = (page_obj['page']//facteur) + random_num +1 
    time.sleep(temps)
    
    #  stocker les avis par entreprise
    noms_entreprises=[]
    noms = []
    nombres_avis = []
    pays_list = []
    notes = []
    dates = []
    titres_avis = []
    contenus_avis = []
    reponses_entrprises = []
    
    # Construction de l'URL pour chaque page
    url = f"{page_obj['base_url']}?page={page_obj['page']}"
    
    print(f"\tPage numéro {page_obj['page']}")
    # au cas où il y a la réponse de requests n eqaule 200// des erreurs à eviter 
    try:
        response = requests.get(url, page_obj['headers'])
        if response.status_code == 200:
            # Récupération du contenu de la page
            Soup = ps(response.content, 'lxml')

            # Recherche des avis clients sur la page
            avis_Clients = Soup.find_all('article', class_='paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_reviewCard__hcAvl')

            for avis in avis_Clients:

                # Extraction et ajout des données pour chaque avis
                nom = avis.find('span', {'data-consumer-name-typography': True}).text.strip() if avis.find('span', {'data-consumer-name-typography': True}) else 'Non'
                nombre_avis = avis.find('span', {'data-consumer-reviews-count-typography': True}).text.split(' ')[0] if avis.find('span', {'data-consumer-reviews-count-typography': True}) else '0'

                svg = avis.find('svg')
                if svg and svg.find_next_sibling('span'):
                    pays = svg.find_next_sibling('span').text.strip()
                else:
                    pays = 'Non'

                note_img = avis.find('div', class_='star-rating_starRating__4rrcf')
                if note_img and note_img.find('img', alt=True):
                    note_alt_text = note_img.find('img', alt=True)['alt']
                    note = note_alt_text.replace('Noté ', '').replace(' sur 5 étoiles', '')
                else:
                    note = 'Non'

                date = avis.find('time')['datetime']
                titre_avis = avis.find('h2').text.strip() if avis.find('h2') else 'Non'
                contenu_avis = avis.find('p', {'data-service-review-text-typography': True}).text.strip() if avis.find('p', {'data-service-review-text-typography': True}) else 'Non'

                reponse_entreprise_element = avis.find('p', class_='styles_message__shHhX')
                reponse_entreprise = reponse_entreprise_element.text.strip() if reponse_entreprise_element else 'Non'

                noms_entreprises.append(page_obj['entreprise'])
                noms.append(nom)
                nombres_avis.append(nombre_avis)
                pays_list.append(pays)
                notes.append(note)
                dates.append(date)
                titres_avis.append(titre_avis)
                contenus_avis.append(contenu_avis)
                reponses_entrprises.append(reponse_entreprise) 
                
        else:
            print(f"\t\tErreur lors de la requête de la Page {page_obj['page']}: {response.status_code}")
            time.sleep(10)
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {url}: {e}")
    
    return pd.DataFrame({
    "Nom_Entreprise": noms_entreprises,  
    "Nom_Client": noms,
    "Nombre_avis": nombres_avis,
    "Pays": pays_list,
    "Note": notes,
    "Date": dates,
    "Titre_avis": titres_avis,
    "Contenu_avis": contenus_avis,
    "Réponse_Entrpris": reponses_entrprises
    })
            
             
def scrapper_les_avis(row, csv_directory):
    
    base_url = row['Url']
    nombre_de_pages = row['NombreAvis']//20 + 1
    entreprise = row['Entreprise']
    users_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1.0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
                    "Mozilla/5.0 (Linux; Android 13; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36"]
    pages_objs = []
    
    print(f"Début du scrapping des avis de l'entreprise {entreprise}.\nUrl: {base_url}\nNombre d'avis = {row['NombreAvis']}\nNombres de pages = {nombre_de_pages} à raison de 20 avis par page.")
    
    for page in range(1, nombre_de_pages + 1):
        
        pages_objs.append({
            'entreprise': entreprise,
            'base_url': base_url,
            'page': page,
            'headers': {'User-Agent': random.choice(users_agents)}
            
        })
        
    # Determine the number of processes to use
    num_processes = multiprocessing.cpu_count()
    print(f"Le numéro de processeur est de {num_processes}")

    # Create a pool of processes
    pool = multiprocessing.Pool(processes=(num_processes-1))
    
    # Apply worker_function to each element in parallel
    results = pool.map(scrapper_les_avis_par_pages, pages_objs, 1)

    # Close the pool when you're done
    pool.close()
    pool.join()
    
    # Création d'un DataFrame pour chaque entreprise
    df_avis = pd.concat(results, ignore_index=True)

    df_avis = df_avis.astype({
    "Nom_Entreprise": 'object',  
    "Nom_Client": 'object',
    "Nombre_avis": 'int64',
    "Pays": 'object',
    "Note": 'int64',
    "Date": 'object',
    "Titre_avis": 'object',
    "Contenu_avis": 'object',
    "Réponse_Entrpris": 'object'
    })
    
    print(df_avis.head())

    # Check if directory already exists (optional)
    if os.path.exists(csv_directory) == False:
        
        # Create the directory
        os.makedirs(csv_directory)
    
    # Sauvegarde du DataFrame dans un fichier CSV
    df_avis.to_csv(f"{csv_directory}/avis_{entreprise}.csv", index=False)
    del(df_avis)
    print(f"Fin du scrapping des avis de l'entreprise {entreprise}.\n")
    
    # Pour eviter la détection un volume anormalement élevé de requêtes provenant de mon adresse IP 
    time.sleep(20)
    


if __name__ == '__main__':

    base_dir = "scrapping_results"
    base_dir = create_dir_with_timestamp(base_dir)
    csv_directory = f"{base_dir}/avis" 
    output_file = f"{base_dir}/avis.csv"
    
    scrapper_les_entreprises(base_dir)
    df_entreprises = pd.read_csv(f'{base_dir}/entreprises.csv')
    df_entreprises = df_entreprises[df_entreprises["NombreAvis"] > 0]
    df_entreprises = df_entreprises.sort_values("NombreAvis")

    # run scrapper (itertuples for efficiency)
    for _, row in df_entreprises.iterrows():
        scrapper_les_avis(row, csv_directory)

    unify_csv_files(csv_directory, output_file)