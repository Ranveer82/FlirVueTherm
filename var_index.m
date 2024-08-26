function var_index(matFilePath, desiredKey)

% Load the .mat file
data = load(matFilePath);

% Get all the variable names from the loaded .mat file
variableNames = fieldnames(data);

% Search for the desired key in the variable names
matchingKey = '';
for i = 1:numel(variableNames)
    if strcmp(variableNames{i}, desiredKey)
        matchingKey = variableNames{i};
        break;
    end
end

% Check if a matching key was found
if ~isempty(matchingKey)
    % Access the value corresponding to the matching key
    matchingValue = data.(matchingKey);
    
    % Display the value
    disp(matchingValue);
else
    % No matching key found
    disp('No matching key found.');
end

end
