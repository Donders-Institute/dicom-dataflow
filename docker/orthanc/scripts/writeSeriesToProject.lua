TARGET = '/project'

function ToAscii(s)
   -- http://www.lua.org/manual/5.1/manual.html#pdf-string.gsub
   return s:gsub('[^a-zA-Z0-9-/ ]', '_')
end

function DirExists(strFolderName)
   -- what a creative way to check whether the directory exists, LUA sucks!!
   local f = io.popen("if [ -d " .. strFolderName .. " ]; then echo 1; else echo 0; fi", 'r')
   local o = f:read("*a")
   f:close()

   if string.match(o, '^1.-') then
      print("directory " .. strFolderName .. " exists") 
      return true
   else
      print("directory " .. strFolderName .. " does not exists")
      return false
   end
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

   local projectDir = TARGET .. '/' .. t[1]

   print('Writing stable series ' .. seriesId .. ' to project: ' .. t[1])

   if DirExists(projectDir) then

      -- compose path to path of the image instance
      local path = projectDir .. '/raw/mri/' ..
                   t[2] .. '/' ..
                   study['StudyID'] .. '/' ..
                   string.format("%02d", series['SeriesNumber']) .. '_' .. ToAscii(series['SeriesDescription'])
 
      for i, instance in pairs(instances) do
      
         local tags = ParseJson(RestApiGet('/instances/' .. instance)) ['MainDicomTags']
 
         -- Retrieve the DICOM file from Orthanc
         local dicom = RestApiGet('/instances/' .. instance .. '/file')
 
         -- Create the subdirectory (CAUTION: For Linux demo only, this is insecure!)
         -- http://stackoverflow.com/a/16029744/881731
         os.execute('mkdir -p "' .. path .. '"')
 
         -- Compose absolute file name 
         local fname = path .. '/' .. string.format("%05d", tags['InstanceNumber']) .. '_' .. tags['SOPInstanceUID'] .. '.IMA'
 
         -- Write to the file
         local target = assert(io.open(fname, 'wb'))
         target:write(dicom)
         target:close()
      end

   else
       print('project directory ' .. projectDir .. ' not exist, skipped.')
   end
end
