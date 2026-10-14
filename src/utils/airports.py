airports_zone1 = [
       'BNC', 'BZV', 'EBB', 'FBM', 'FIH', 
       'FKI', 'FMI', 'GMA', 'GOM', 'ION', 
       'JUB', 'KGA', 'KHX', 'KND', 'KSE', 
       'KWZ', 'KXO', 'MAK', 'MDK', 'MJM', 
       'OUE', 'PNR', 'RUA', 'WUU', 'BUX', 
       'IRP', 'BDT', 'MNB', 'RUE'
       ]

airports_drc = [
       'FBM', 'FIH', 'FKI', 'FMI',
       'GMA', 'GOM', 'KGA', 'KND', 
       'KWZ', 'MDK', 'MJM', 'BNC', 
       'BUX', 'IRP', 'BDT', 'MNB', 'RUE',
       ]

airports_uga = ['EBB', 'KHX', 'KXO', 'RUA', 'KSE', 'PAF']


# zone 1 airport coordinates
# airport code : (latitude, longitude)
# taken from: https://ourairports.com/airports/
coordinates = {
       # DRC
       'BNC' : (0.575000  , 29.473900), 
       'FBM' : (-11.591494, 27.530753), 
       'FIH' : (-4.385750 , 15.444600), 
       'FKI' : (0.481639  , 25.337999),      
       'FMI' : (-5.875560 , 29.250000),          
       'GMA' : (3.235370  , 19.771299),       
       'GOM' : (-1.666758 , 29.238037),         
       'KGA' : (-5.900050 , 22.469200),       
       'KND' : (-2.919180 , 25.915400),     
       'MDK' : (0.022600  , 18.288700),            
       'MJM' : (-6.121240 , 23.569000),        
       'BUX' : (1.565743  , 30.220685),        
       'IRP' : (2.827610  , 27.588301),     
       'RUE' : (0.117142  , 29.312992),

       # Congo
       'BZV' : (-4.251700 , 15.253000), 
       'ION' : (1.589968  , 18.046624),        
       'OUE' : (1.615990  , 16.037901),       
       'PNR' : (-4.816030 , 11.886600),   
       'BDT' : (4.252745  , 20.975271),    
       'MNB' : (-5.930637 , 12.351334),                  
       
       # Uganda
       'EBB' : (0.042386  , 32.443501), 
       'KHX' : (-0.716500 , 29.699700),        
       'KSE' : (0.183000  , 30.100000),        
       'KWZ' : (-10.765900, 25.505699),      
       'KXO' : (-1.283700 , 29.719700),       
       'RUA' : (3.049152  , 30.911714),           

       # South Sudan
       'JUB' : (4.872010  , 31.601101),
       'MAK' : (9.558739  , 31.651937),
       'WUU' : (7.725830  , 27.975000),                

       # Burundi

       # Rwanda

}