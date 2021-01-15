# CoastSat.PlanetScope

Yarran Doherty, UNSW Water Research Laboratory, 01/2021


## **Description**

CoastSat.PlanetScope is an open-source extension to the python toolkit CoastSat enabling users to extract time-series of shoreline position from PlanetScope Dove satellite imagery. Similar to CoastSat, the CoastSat.PlanetScope extension utilises a machine-learning shoreline detection algorithm to classify images into sand, water, whitewater and other pixel classes prior to a sub-pixel shoreline extraction process. An additional co-registration step is implemented to minimise the impact of geo-location errors. Transect intersection and a tidal correction  based on a generic beach slope is then applied to provide a time-series of shoreline position. 

![](readme_files/extraction.png)

Output files include:
- Shoreline timeseries .geojson file for use in GIS software (no tidal correction)
- Tidally corrected shoreline transect intersection time-series csv
- Tidally corrected transect timeseries plots


## **Installation**

The CoastSat.PlanetScope toolkit is run in the original CoastSat environment. Refer CoastSat installation instructions 1.1. [https://github.com/kvos/CoastSat]. 

Additional packages to manually install in the coastsat environment are:
- Rasterio [pip install rasterio]
- AROSICS (if co-registration step is included) [https://danschef.git-pages.gfz-potsdam.de/arosics/doc/installation.html]

## **Usage**

It is recommended the toolkit be run in spyder. Ensure spyder graphics backend is set to 'automatic'
- Preferences - iPython console - Graphics - Graphics Backend - Automatic

CoastSat.PlanetScope is run from the CoastSat_PS.py file. Instructions and comments are provided in this file for each step. It is recommended steps be run as individual cells for first time users. 

PlanetScope images need to be manually downloaded by the user. It is recommended this be done using the QGIS Planet plugin [https://developers.planet.com/docs/integrations/qgis/quickstart/] and cropped to a user area of interest to reduce file size prior to download. To run CoastSat.PlanetScope, keep all downloaded images and associated metadata in a single folder and direct CoastSat.PlanetScope to this folder in the CoastSat_PS.py settings.

Settings and interactive steps are based on the CoastSat workflow and will be familiar to users of CoastSat. 

All user input files (area_of_interest_polygon.kml, transects.geojson & tide_data.csv) should be saved in the folder "...CoastSat.PlanetScope/user_inputs"
- Analysis region of interest .kml file can be selected and downloaded from [geojson.io]. 
- Transects .geojson file (optional) should match the user input settings epsg. If skipped, transects may be drawn manually with an interactive popup. Alternately, the provided NARRA_transect.geojson file may be manually modified in a text editor to add/remove/update transect names, coordinates and epsg
- Tide data .csv for tidal correction (optional) should be in UTC time and local mean sea level (MSL) elevation

Interactive popup window steps include:
- 1. Raw PlanetScope reference image selection for co-registration (step 1.2.)
- 2. Top of Atmosphere merged reference image selection for shoreline extraction (step 2.1.)
- 3. Reference shoreline digitisation (refer 'Reference shoreline' section of CoastSat readme for example) - (step 2.1.)
- 4. Transect digitisation (optional - only if no transects.geojson file provided) - (step 2.1.)
- 5. Manual error detection (optional - keep/discard popup window as per CoastSat - (step 3.)

Beach slopes for the tidal correction can be extracted using the CoastSat.Slope toolkit [https://github.com/kvos/CoastSat.slope]


## **Training Neural-Network Classifier**

Due to the preliminary stage of testing, validation has only been completed at Narrabeen-Collaroy (Sydney, Australia). As such, the NN classifier is optimised for this site and may perform poorly at sites with differing sediment composition. It is recommended a new classifier be trained for such sites. 

Steps are provided in "...CoastSat.PlanetScope/coastsat_ps/classifier/train_new_classifier.py". Instructions are provided in this file and are based of the CoastSat classifier training methods [https://github.com/kvos/CoastSat/blob/master/doc/train_new_classifier.md]. CoastSat.PlanetScope must be run up to/including step 1.3. on a set of images to extract co-registered and top of atmosphere corrected images for classifier training. 


## **Validation Results**

Accuracy validated against in-situ RTK-GPS survey data at Narrabeen-Collaroy beach in the Northen beaches of Sydney, Australia with a RMSE of 3.66m (n=438). 

An equivelent validation study at Duck, North Carolina, USA provided an observed RMSE error of 4.74m (n=167). 


Detailed results and methodology outlined in:

Doherty Y., Harley M.D., Vos K., Splinter K.D. (2021). Evaluation of PlanetScope Dove Satellite Imagery for High-Resolution, Near-Daily Shoreline Monitoring (in peer-review)


