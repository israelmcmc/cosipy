.. role:: raw-html-m2r(raw)
   :format: html


```mermaid
%%{init: {'theme':'default'}}%%
graph TD;
    A[Data_Challenge] --- B[Setup] & C[Input_Files] & D[Run_Data_Challenge] & E[Source_Library\ :raw-html-m2r:`<br>`\ master_source_list.txt] & F[Examples];
    B --- Ba(setup.py);
    C --- Ca["Orientation_Files"];
    C --- Cb[Geometry_Files];
    C --- Cd[Configuration_Files];
    C --- Ce["Transmission_Probability"];
    D --- Da(run_data_challenge.py\ :raw-html-m2r:`<br>`\ make_orientation_bins.py\ :raw-html-m2r:`<br>`\ ExtractImage.cxx\ :raw-html-m2r:`<br>`\ ExtractLightCurve.cxx\ :raw-html-m2r:`<br>`\ ExtractSpectrum.cxx);
    E --- Ea[Source1];
    E --- Eb[Source2];
    E --- Ec[SourceN];
    E --- Ed[Make_Sources];
    Ea --- Eaa(source1.source\ :raw-html-m2r:`<br>`\ source1_spec.dat\ :raw-html-m2r:`<br>`\ source1_LC.dat\ :raw-html-m2r:`<br>`\ source1_pol.dat);
    Eb --- Ebb(source2.source\ :raw-html-m2r:`<br>`\ source2_spec.dat\ :raw-html-m2r:`<br>`\ source2_LC.dat\ :raw-html-m2r:`<br>`\ source2_pol.dat);
    Ec --- Ecc(sourceN.source\ :raw-html-m2r:`<br>`\ sourceN_spec.dat\ :raw-html-m2r:`<br>`\ sourceN_LC.dat\ :raw-html-m2r:`<br>`\ sourceN_pol.dat);
    Ed --- Edd(make_sources.py);
