function OnStoredInstance(instanceId, tags, metadata)
   -- Extract the value of the "PatientName" DICOM tag
   local patientID = string.upper(tags['PatientID'])
   
   if string.find(patientID, 'RUNDMCSI') ~= nil then
       -- routing DICOM images collected by Annemieke ter Telgte to PASC-ISD
       SendToModality(instanceId, 'PACS-ISD')
   end
end
