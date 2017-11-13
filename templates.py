batchl2bin = '''#!/bin/sh
# to run it: ./batchl2bin.bsh
# first define the region to be extracted from your MODIS L1A files
# NOTE! change these for your own region of interest
export OCSSWROOT={SEADAS_PATH}
source $OCSSWROOT/OCSSW_bash.env
cd {directory}

mkdir afterrun

for FILE in originals/*L2_LAC_OC*
do
  # The line below assumes an extension, and creates a base name without that extension
  BASE=`echo $FILE |awk -F. '{{ print $1 }}'`

  L2FILE=${{BASE}}.L2_LAC_OC.nc
  L3FILE=${{BASE##*/}}.L3_LAC_OC

  # process the L2 file to L3
  echo "Processing $L2FILE to Level 3..."
  # NOTE! customize the l2gen parameters here
  l2bin infile=$L2FILE ofile=$L3FILE \
  resolve=1 flaguse=[''] l3bprod='chlor_a'

done

mv *.L2_LAC_*.nc afterrun/
echo "Done batchl2bin."
'''

batchl3bin = '''#!/bin/sh
export OCSSWROOT={SEADAS_PATH}
source $OCSSWROOT/OCSSW_bash.env
cd {directory}
# NOTE! change these for your own region of interest

# to run: ./batchl3bin.bsh

# Update the coordinates
# Write the list of days
# Update the correct year of the run

SWLON={west}
SWLAT={south}
NELON={east}
NELAT={north}

for DAYINYEAR in {days_in_year}
do
thisDay=$DAYINYEAR
echo "$thisDay"
rm list*.txt
for FILE in *${{DAYINYEAR}}*L3_LAC_OC*
do
echo $FILE >> list_oc.txt
done

inListOC="list_oc.txt"


# The line below assumes an extension, and creates a base name without that extension
        BASE1="A{year}${{thisDay}}"
        L3FILE=${{BASE1}}*.L3_LAC_OC
        L3FILEBinned=${{BASE1}}.L3b_GAC_OC

        # process the L2 file to L3
        echo "Processing $L3FILE to Level 3 binned..."
        # NOTE! customize the l2gen parameters here "chlor_a,pic,par,nflh"
        l3bin in=$inListOC ofile=$L3FILEBinned \
        out_parm="chlor_a" \
        loneast=$NELON lonwest=$SWLON \
        latnorth=$NELAT latsouth=$SWLAT

done
echo "Done batchl3bin."
'''

batchl3mapgen = '''#!/bin/bash
export OCSSWROOT={SEADAS_PATH}
source $OCSSWROOT/OCSSW_bash.env
cd {directory}
# to run: ./batchl3mapgen.bsh

# Update the coordinates!

# first define the region to be extracted from your MODIS L1A files
# NOTE! change these for your own region of interest
SWLON={west}
SWLAT={south}
NELON={east}
NELAT={north}

for FILE in *L3b_GAC_OC*
do
  # The line below assumes an extension, and creates a base name without that extension
  BASE=`echo $FILE |awk -F. '{{ print $1 }}'`
  # BASE1=${{BASE:0:8}}
  # echo $BASE1
  L3FILE=${{BASE}}.L3b_GAC_OC #.main
  # L3FILEMapCHL=${{BASE}}.L3m_DAY_CHL_chlor_a_1km.nc
  L3FILEMapOC=${{BASE}}.L3m_DAY_OC_1km.nc

  # process the L2 file to L3
  echo "Processing $L3FILE to a chl map..."
  # NOTE! customize the l2gen parameters here
  l3mapgen ifile=$L3FILE ofile=$L3FILEMapOC \
  product='chlor_a' \
  resolution=1km \
  east=$NELON west=$SWLON \
  north=$NELAT south=$SWLAT \

done

mkdir OC_maps
mv *.L3b_GAC* afterrun/
mv *1km.nc OC_maps
'''

batchSmigen = '''
#!/bin/bash
export OCSSWROOT={SEADAS_PATH}
source $OCSSWROOT/OCSSW_bash.env
cd {directory}
# to run: ./batchSmigen.bsh
# Update the coordinates!

# first define the region to be extracted from your MODIS L1A files
# NOTE! change these for your own region of interest
SWLON={west}
SWLAT={south}
NELON={east}
NELAT={north}

for FILE in *L3b_GAC_OC*
do
  # The line below assumes an extension, and creates a base name without that extension
  L3FILE=${{BASE}}.L3b_GAC_OC # .main
  L3FILEMapCHL=${{BASE}}.L3m_DAY_CHL_chlor_a_1km.nc
  L3FILEMapPIC=${{BASE}}.L3m_DAY_PIC_1km.nc
  L3FILEMapIPAR=${{BASE}}.L3m_DAY_IPAR_1km.nc
  L3FILEMapNFLH=${{BASE}}.L3m_DAY_NFLH_1km.nc

  # process the L2 file to L3
  echo "Processing $L3FILE to a chl map..."
  # NOTE! customize the l2gen parameters here
  smigen ifile=$L3FILE ofile=$L3FILEMapCHL \
  prod='chlor_a' \
  loneast=$NELON lonwest=$SWLON \
  latnorth=$NELAT latsouth=$SWLAT \
  projection=RECT resolution=1km precision=F
done

mv *.L3b_GAC_* afterrun/
mv *.L3_LAC_* afterrun/
mkdir OC_maps
mv *1km.nc OC_maps

echo "Done batchSmigen"
'''
