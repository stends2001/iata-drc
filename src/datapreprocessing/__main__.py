import pandas as pd

from ..utils import PathManager
from .shapedata.capitals import raw_capitals, preprocess_capitals
from .shapedata.countries import load_raw_shapedata
from .mobility import load_single_raw_iata, preprocess_single_iata_data
from .epidemiology import load_raw_case_data, process_case_data
from .other import load_raw_population_data_uga, load_raw_population_data_drc, process_population_data_drc, process_population_data_uga
from .utils import save_gdf, save_df

if __name__ == '__main__':
    pm = PathManager()

    ##############
    # SHAPE DATA #
    ##############

    # capitals
    capitals_raw = raw_capitals(pm.data / 'raw' / 'shapedata' / 'country-capital-lat-long-population.csv')
    capitals_pcd = preprocess_capitals(capitals_raw)
    
    save_gdf(capitals_pcd,
             pm.data / 'processed' / 'shapedata' / "shared" / "capitals.shp",
             )

    # countries
    countries_raw = load_raw_shapedata(pm.data / 'raw' / 'shapedata')
    countries_pcd = {countryname : shp.process() for countryname, shp in countries_raw.items()}

    for countryname, countryshape in countries_pcd.items():
        output_path = pm.data / 'processed' / 'shapedata' / countryname / f"{countryname}.shp"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_gdf(countryshape.shp,
                 output_path)

    #############
    # CASE DATA #
    #############
    casedata_raw = load_raw_case_data(pm.data / 'raw' / 'other' / 'cases.csv')
    casedata_pcd = process_case_data(casedata_raw)

    save_df(casedata_pcd,
             pm.data / 'processed' / 'epidemiology' / "cases.csv"            
            )    

    ###################
    # POPULATION DATA #
    ###################
    population_drc_raw = load_raw_population_data_drc(
        pm.data / 'raw' / 'other' / 'drc-hpc-projection-population-2024.xlsx'
        )

    population_uga_raw = load_raw_population_data_uga(
        pm.data/'raw'/ 'other'/ 'uga_admpop_2023.xlsx'    
    )

    population_drc_pcd = process_population_data_drc(population_drc_raw)
    population_uga_pcd = process_population_data_uga(population_uga_raw)    

    save_df(population_drc_pcd,
             pm.data / 'processed' / 'other' / "population_drc.csv"            
            )

    save_df(population_uga_pcd,
             pm.data / 'processed' / 'other' / "population_uga.csv"            
            )


    #################
    # MOBILITY DATA #
    #################

    # iata - zone -in
    zone_in1 = preprocess_single_iata_data(load_single_raw_iata(pm.data / 'raw' / 'iata' / 'zone_in_2025.csv'))
    zone_in2 = preprocess_single_iata_data(load_single_raw_iata(pm.data / 'raw' / 'iata' / 'zone_in_2026.csv'))
    zone_in  = pd.concat([zone_in1, zone_in2], axis =0)

    save_df(zone_in,
             pm.data / 'processed' / 'mobility' / "iata_zone_in.csv"            
            )

    # iata - zone -out
    zone_out1= preprocess_single_iata_data(load_single_raw_iata(pm.data / 'raw' / 'iata' / 'zone_out_2025_1.csv'))
    zone_out2= preprocess_single_iata_data(load_single_raw_iata(pm.data / 'raw' / 'iata' / 'zone_out_2025_2.csv'))
    zone_out3= preprocess_single_iata_data(load_single_raw_iata(pm.data / 'raw' / 'iata' / 'zone_out_2026_1.csv'))
    zone_out4= preprocess_single_iata_data(load_single_raw_iata(pm.data / 'raw' / 'iata' / 'zone_out_2026_2.csv'))    
    zone_out  = pd.concat([zone_out1, zone_out2, zone_out3, zone_out4], axis =0)

    save_df(zone_out,
             pm.data / 'processed' / 'mobility' / "iata_zone_out.csv"            
            )
