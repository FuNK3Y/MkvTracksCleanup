from couchpotato.core.event import addEvent
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
import os
import subprocess
import re
import shutil

log = CPLog(__name__)

class MkvTracksCleanup(Plugin):
   def __init__(self):
      self.mkvmergeUILanguage='en' if os.name=='nt' else 'en_US'
      addEvent('renamer.after', self.callMkvTracksCleanup, priority = 90)
   def stringToList(self,s):
      return [i.strip().lower() for i in s.split(',')]
   def cleanupMkv(self, sourcePath, sourceFolder, renamerFileName):
      tracks=[]
      # Gather tracks infos
      info=subprocess.check_output(['mkvmerge','--ui-language',self.mkvmergeUILanguage,'--identify-verbose',sourcePath])
      for trackStr in info.split('\n'):
         match=re.search(r'Track ID (\d+): (.+?) .+codec_id:(.+?) .+language:(.+?) ',trackStr)
         if(match):
            tracks.append({'Id':match.group(1),'Type':match.group(2),'Codec':match.group(3),'Language':match.group(4)})

      # Filter the tracks   
      filteredAudioTracks=[]
      audioCodecPreference=[("A_"+i.strip()).lower() if i!='' else '' for i in self.conf('audio_codec_preference').split(',')]
      for l in self.stringToList(self.conf('audio_languages')):
         filteredAudioTracks.extend(sorted(filter(lambda t: t['Language']==l and t['Type']=='audio',tracks),key=lambda t: audioCodecPreference.index(t['Codec'].lower()) if t['Codec'].lower() in audioCodecPreference else float('inf'))[0:self.conf('max_audio_track_per_language')])
      filteredSubtitleTracks=[]
      for l in self.stringToList(self.conf('subtitle_languages')):
         filteredSubtitleTracks.extend(filter(lambda t: t['Language']==l and t['Type']=='subtitles',tracks)[0:self.conf('max_subtitle_track_per_language')])
      
      # Variable used for new name generation
      language=self.conf('language_separator').join(set(t['Language'].upper() for t in (filteredAudioTracks if len(filteredAudioTracks)>=1 else filter(lambda t: t['Type']=='audio',tracks))))
      sourceFileName=os.path.split(sourcePath)[1]
      title=os.path.splitext(sourceFileName)[0]
      targetFolder=self.getTargetFolder(os.path.split(sourceFolder)[1],language)
      targetPath=os.path.join(targetFolder,self.getTargetFileName(sourceFileName,renamerFileName,language))
      if not os.path.isdir(targetFolder):
         os.mkdir(targetFolder)
      # Call the cleanup through mkvmerge
      mkvmergeCall=['mkvmerge','--ui-language',self.mkvmergeUILanguage,'--output',targetPath,'--title',title]
      if len(filteredSubtitleTracks) > 0:
         mkvmergeCall+=["--subtitle-tracks",",".join(str(t['Id']) for t in filteredSubtitleTracks)]
      else:
         mkvmergeCall+=["--no-subtitles"]
      if len(filteredAudioTracks) > 0:
         mkvmergeCall+=["--audio-tracks",",".join(str(t['Id']) for t in filteredAudioTracks)]
         for i in range(len(filteredAudioTracks)):
            mkvmergeCall.extend(["--default-track", ":".join([str(filteredAudioTracks[i]['Id']), "0" if i else "1"])])
      mkvmergeCall+=[sourcePath]
      log.info('mkvmerge call parameters: '+str(mkvmergeCall))
      return subprocess.call(mkvmergeCall),language,targetFolder,targetPath
   def getTargetFileName(self,name,renamerFileName,language):
      newName=self.conf('target_file_naming_pattern').replace('<filename>',renamerFileName).replace('<language>',language).strip()
      base,ext=os.path.splitext(name.replace(renamerFileName,newName))
      return base+ext.lower()
   def getTargetFolder(self,name,language):
      targetFolderName=self.conf('target_folder_naming_pattern').replace('<foldername>',name).replace('<language>',language)
      return os.path.join(self.conf('to'),targetFolderName).strip()
   def callMkvTracksCleanup(self, message = None, group = None):
      if not self.conf('enabled'):
         return
      renamedFiles=group['renamed_files']
      sourceFolder=group['destination_dir']
      renamerFileName=group['filename']
      movedFiles=[]
      language=""
      targetFolder=self.getTargetFolder(os.path.split(sourceFolder)[1],language)
      returnCode=0
      for m in sorted(renamedFiles, key=lambda m : os.path.splitext(m)[1].lower()!='.mkv'):
         if os.path.splitext(m)[1].lower()=='.mkv':
            log.info('Starting cleanup of: '+m)
            lastReturnCode,language,targetFolder,targetPath=self.cleanupMkv(m,sourceFolder,renamerFileName)
            returnCode+=lastReturnCode
            if not lastReturnCode:
               log.info('Cleanup completed for: '+m)
            else:
               log.error('Could not clean tracks for: '+m)
         else:
            targetPath=os.path.join(targetFolder,self.getTargetFileName(os.path.split(m)[1],renamerFileName,language))
            log.info('Not a mkv, will be moved from '+m+' to '+targetPath)
            if not os.path.isdir(targetFolder):
               os.mkdir(targetFolder)
            shutil.copy(m,targetPath)
         movedFiles.append(targetPath)
      if self.conf('remove_source_folder'):
         if returnCode == 0:
            shutil.rmtree(sourceFolder)
         else:
            log.error('Something went wrong with one if those files, manual cleanup needed: '+str(renamedFiles))
      # Change group parameter so couchpotato scan the new location
      group['renamed_files']=movedFiles
      group['destination_dir']=targetFolder
      group['filename']=self.getTargetFileName(renamerFileName,renamerFileName,language)
