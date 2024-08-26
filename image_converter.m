import rJPEG2TIFF_ranveer.*
% import matchingvalue.*
% Specify the folder path where the JPEG files are located
folder = 'C:\Users\kumar\OneDrive\Desktop\DRONE\06_Yamuna_sd\TIR_Rjpeg\20221206_090054';

% Get a list of all JPEG files in the folder
fileList = dir(fullfile(folder, '*.jpg'));

% Loop through each file
for i = 1:length(fileList)
    filename = fileList(i).name;
    rJPEG2TIFF_ranveer(strcat(folder,'\',filename ));
    disp(filename);
end


% exif_data = rJPEG2TIFF_ranveer('C:\Users\kumar\OneDrive\Desktop\DRONE\20221201_063539_R.jpg','emissivity',0.97,'distance',50,'Ta',27,'Tr',33,'RH',50);
% matchingValue = matchingvalue(exif_data, 'File Name');
% disp(matchingValue)