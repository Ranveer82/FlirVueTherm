function rJPEG2TIFF(filename,varargin)
%RJPEGREAD reads Radiometric JPEG files acquired using FLIR thermal cameras
%   rJPEG2TIFF(FILENAME,VARARGIN) reads a radiometric JPEG file acquired 
%   with a FLIR thermal camera into a MATLAB matrix and converts to 32-bit 
%   TIFF.
%   File and path is specified as a string using FILENAME. Optional input 
%   arguments define parameters used for atmospheric and radiometric 
%   correction.
%
%   If optional input arguments are not used, the default values set at the
%   time of image aquisition will be used.
%
%   Uses Exiftool (http://www.sno.phy.queensu.ca/~phil/exiftool/) to
%   process the rJPEG image.  Exiftool.exe must therefore be present in the 
%   same folder as this function.
%
%   See Exiftool forum (http://u88.n24.queensu.ca/exiftool/forum/index.php/
%   topic,4898.45.html) for links to FLIR documentation containing
%   atmospheric transmission/radiance formulae
%
%   Optional input arguments: 
%
%   'emissitivity'  - emissivity of object being imaged (0 - 1)
%   'distance'      - distance of object being imaged (in metres)
%   'Tr'            - reflected temperature of object (in degrees C; generally OK to set this value to the same as the ambient air temperature unless imaging reflective surfaces (ie. metals)
%   'Ta'            - air/atmospheric temperature (in degrees C)
%   'RH'            - relative humidity (as %)
%
%   Usage: rJPEG2TIFF('TIR0001.jpg','emissivity',0.97,'distance',100,'Ta',15,'Tr',15,'RH',75);
%
%   (c) Steve Dugdale, 2017-07-24

%parse inputs
[emissivity distance Ta Tr RH] = parse_inputs(varargin);

%extract exif data from file and put into table
[~,exifdata] = system(['exiftool "',filename,'"',]); %get exif data from RJPEG
exifdata=strsplit(exifdata,'\n');
exifdata=exifdata';
exifdata(end,:)=[];
exifdata = regexp(exifdata, ':', 'split', 'once');
exifdata = strtrim(exifdata);
for n=1:numel(exifdata);
    exifdata(n,1:2)=exifdata{n};
end

%load raw thermal image
system(['exiftool -b -rawthermalimage "',filename,'" > tempImage.tif']); %extract binary from RJPEG to temporary tiff
uTot=imread('tempImage.tif','tif'); %load temporary image
delete('tempImage.tif'); %delete temporary image
uTot=double(uTot);


%extract data for radiometric computations (unless already entered as variables)
if isempty(emissivity);emissivity=str2num(exifdata{65,2});end %get emissivity
if isempty(distance);distance=strsplit(exifdata{66,2});distance=str2num(distance{1});end %get object distance
if isempty(Tr);Tr=strsplit(exifdata{67,2});Tr=str2num(Tr{1});end %get reflected temperature
if isempty(Ta);Ta=strsplit(exifdata{68,2});Ta=str2num(Ta{1});end %get atmospheric temperature
if isempty(RH);RH=strsplit(exifdata{71,2});RH=str2num(RH{1});end %get relative humidity

%extract Planck formula constants (determined when camera was calibrated by FLIR)
B=str2num(exifdata{73,2}); %get Planck B
F=str2num(exifdata{74,2}); %get Planck F
O=str2num(exifdata{99,2}); %get Planck O
R1=str2num(exifdata{72,2}); %get Planck R1
R2=str2num(exifdata{100,2}); %get Planck R2

%extract atmospheric (determined when camera was calibrated by FLIR)
A1=str2num(exifdata{75,2}); %get Atmospheric Transmissivity Alpha 1
A2=str2num(exifdata{76,2}); %get Atmospheric Transmissivity Alpha 2
B1=str2num(exifdata{77,2}); %get Atmospheric Transmissivity Beta 1
B2=str2num(exifdata{78,2}); %get Atmospheric Transmissivity Beta 2
X=str2num(exifdata{79,2}); %%get Atmospheric Transmissivity X

%calculate atmospheric transmission
H2O = (RH/100) * exp(1.5587 + 6.939e-2 * Ta - 2.7816e-4 * Ta^2 + 6.8455e-7 * Ta^2);
tau = X * exp(-sqrt(distance) * (A1 + B1 * sqrt(H2O))) + (1-X) * exp(-sqrt(distance) * (A2 + B2 * sqrt(H2O)));

%get atmospheric emittance
uAtm=R1/(R2*(exp(B/(Ta+273.15))-F))-O; %get atmospheric radiance (in FLIR raw dn) using Planck's law
attAtm=(1-tau)*uAtm; %compute atmospheric emittance

%get object reflectance
uRefl=R1/(R2*(exp(B/(Tr+273.15))-F))-O; %calculate object reflectance (in FLIR raw dn) using Planck's law
attRefl=(1-emissivity)*tau*uRefl; %compute object reflectance

%correct total radiance (in FLIR raw dn) for atmospheric and reflections
uObj=(uTot-attAtm-attRefl)./emissivity./tau;

%convert radiance (in FLIR raw dn) to temperature using Planck's law
img=B./log(R1./(R2.*(uObj+O))+F)-273.15;

%convert image to single
img=single(img);

%get output filename
[pathstr, name, ext] = fileparts(filename);
tifName=[pathstr,filesep,name,'.tif'];

%write TIFF
t = Tiff('x.tif','w'); 
tagstruct.ImageLength = size(img, 1); 
tagstruct.ImageWidth = size(img, 2); 
tagstruct.Compression = Tiff.Compression.LZW; 
tagstruct.SampleFormat = Tiff.SampleFormat.IEEEFP; 
tagstruct.Photometric = Tiff.Photometric.MinIsBlack; 
tagstruct.BitsPerSample = 32; % 32; %set TIFF to 32 bit floating point (necessary to contain true temperature data)
tagstruct.SamplesPerPixel = 1; % 1; 
tagstruct.PlanarConfiguration = Tiff.PlanarConfiguration.Chunky; 
t.setTag(tagstruct); 
t.write(img); 
t.close();
system(['exiftool -TagsFromFile "',filename,'" "-all:all>all:all" "',tifName,'" -overwrite_original']); %append original JPEG metadata to TIFF (important if you want to mosaic TIFFs in Photoscan)

end

function [emissivity distance Ta Tr RH] = parse_inputs(varargin)
varargin=varargin{:};
inputs={'emissivity','distance','Ta','Tr','RH'};
result = arrayfun(@(x) find(arrayfun(@(y) isequal(x,y),varargin),1),inputs,'uni',0);

try emissivity=cell2mat(varargin(result{1}+1)); catch emissivity=[]; end
try distance=cell2mat(varargin(result{2}+1)); catch distance=[]; end
try Ta=cell2mat(varargin(result{3}+1)); catch Ta=[]; end
try Tr=cell2mat(varargin(result{4}+1)); catch Tr=[]; end
try RH=cell2mat(varargin(result{5}+1)); catch RH=[]; end

end



