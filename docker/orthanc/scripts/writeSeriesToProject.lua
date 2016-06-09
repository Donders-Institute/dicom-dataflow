TARGET = '/project'

function ToAscii(s)
   -- http://www.lua.org/manual/5.1/manual.html#pdf-string.gsub
   return s:gsub('[^a-zA-Z0-9-/ ]', '_')
end

function OnStableSeries(seriesId, tags, metadata)

   local instances = ParseJson(RestApiGet('/series/' .. seriesId)) ['Instances']
   local patient = ParseJson(RestApiGet('/series/' .. seriesId .. '/patient')) ['MainDicomTags']
   local study = ParseJson(RestApiGet('/series/' .. seriesId .. '/study')) ['MainDicomTags']
   local series = ParseJson(RestApiGet('/series/' .. seriesId)) ['MainDicomTags']
   -- parse PatientName to get project id
   local t = {}
   local j = 1
   for pp in string.gmatch(patient['PatientID'], "([^_]+)") do
       t[j] = pp
       j = j + 1
   end

   print('Writing stable series ' .. seriesId .. ' to project: ' .. t[1])

   -- compose path to path of the image instance
   local path = TARGET .. '/' .. t[1] .. '/raw/mri/' ..
                t[2] .. '/' ..
                study['StudyID'] .. '/' ..
                ToAscii(series['SeriesDescription'])

   for i, instance in pairs(instances) do
   
      -- Retrieve the DICOM file from Orthanc
      local dicom = RestApiGet('/instances/' .. instance .. '/file')

      -- Create the subdirectory (CAUTION: For Linux demo only, this is insecure!)
      -- http://stackoverflow.com/a/16029744/881731
      os.execute('mkdir -p "' .. path .. '"')

      -- Write to the file
      local target = assert(io.open(path .. '/' .. instance .. '.dcm', 'wb'))
      target:write(dicom)
      target:close()
   end
end
