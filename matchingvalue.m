function value = matchingvalue(cellData, desiredKey)
% GETCELLVALUE - Retrieves a value from a cell array by matching the keys
%
%   VALUE = GETCELLVALUE(CELLDATA, DESIREDKEY) searches for the desired key
%   in the specified cell array and returns the corresponding value.
%
%   Input arguments:
%   - CELLDATA: The cell array containing key-value pairs
%   - DESIREDKEY: The key to match and retrieve the corresponding value
%
%   Output argument:
%   - VALUE: The value corresponding to the matching key, or an empty array
%     if no match is found
%
%   Example usage:
%   data = {'key1', value1, 'key2', value2, 'key3', value3};
%   desiredKey = 'key2';
%   value = getCellValue(data, desiredKey);

% Iterate through the cell array in steps of 2 to access the keys
for i = 1:2:numel(cellData)
    key = cellData{i};
    if strcmp(key, desiredKey)
        value = cellData{i+1};
        return;
    end
end

% No matching key found
value = [];  % or any other appropriate default value

end

% 
% function matchingValue = matchingvalue(matFilePath, desiredKey)
%     % Load the .mat file
%     % data = load(matFilePath);
% 
%     % Get all the variable names from the loaded .mat file
%     variableNames = fieldnames(matFilePath);
% 
%     % Search for the desired key in the variable names
%     matchingKey = '';
%     for i = 1:numel(variableNames)
%         if strcmp(variableNames{i}, desiredKey)
%             matchingKey = variableNames{i};
%             break;
%         end
%     end
% 
%     % Check if a matching key was found
%     if ~isempty(matchingKey)
%         % Access the value corresponding to the matching key
%         matchingValue = data.(matchingKey);
%     else
%         % No matching key found
%         error('No matching key found.');
%     end
% end