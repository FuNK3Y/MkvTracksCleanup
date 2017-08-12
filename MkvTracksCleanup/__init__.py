from .main import MkvTracksCleanup


def autoload():
    return MkvTracksCleanup()

folder_rename_options = {
    'pre': '<',
   'post': '>',
   'choices': {
      'foldername': 'Folder name (defined by the renamer)',
      'language': 'Language',
   },
}
file_rename_options = {
   'pre': '<',
   'post': '>',
   'choices': {
      'filename': 'File name (defined by the renamer)',
      'language': 'Language',
   },
}

config = [{
   'name': 'mkvtrackscleanup',
   'description': 'Remove unwanted tracks from MKV based on languages and codecs',
   'groups': [
      {
         'tab': 'renamer',
         'subtab': 'mkvtrackscleanup',
         'name': 'mkvtrackscleanup',
         'label': 'Remove unwanted tracks from MKVs',
         'options': [
            {
               'name': 'enabled',
               'default': False,
               'type': 'enabler',
            },
            {
               'name': 'to',
               'type': 'directory',
               'description': 'Default folder where the movies are moved to.',
            },
            {
               'name': 'target_folder_naming_pattern',
               'label': 'Folder naming',
               'description': 'Name of the folder',
               'default': '<foldername> <language>',
               'type': 'choice',
               'options': folder_rename_options
            },
            {
               'name': 'target_file_naming_pattern',
               'label': 'File naming',
               'description': 'Name of the file',
               'default': '<filename> <language>',
               'type': 'choice',
               'options': file_rename_options
            },
            {
               'name': 'audio_languages',
               'label': 'Audio languages:',
               'description': ('The list of languages to keep for audio (in order, the favorite first). If no language is matched, every audio track will be kept.','Use mkvmerge documentation to get valid values (case does not matter).'),
               'placeholder': 'Example: eng,fra',
               'default': 'eng',
            },
            {
               'name': 'subtitle_languages',
               'label': 'Subtitle languages:',
               'description': ('The list of languages to keep for subtitle (in order, the favorite first). If no language is matched, no subtitle track will be kept.','Use mkvmerge documentation to get valid values (case does not matter).'),
               'placeholder': 'Example: eng,fra',
               'default': 'eng',
            },
            {
               'name': 'audio_codec_preference',
               'label': 'Audio codec preference:',
               'description': ('Audio codec preference (in order, the favorite first).','The value codec_id from mkvmerge -I will be used (without the A_). Example: dts,ac3,aac (case does not matter)'),
               'placeholder': 'Example: dts,ac3,aac',
               'default': 'dts,ac3',
            },
            {
               'name': 'max_audio_track_per_language',
               'label': 'Max audio tracks per language',
               'type': 'int',
               'description': 'Maximum audio tracks per language.',
               'default': 1,
            },
            {
               'name': 'max_subtitle_track_per_language',
               'label': 'Max subtitle tracks per language',
               'type': 'int',
               'description': 'Maximum subtitle tracks per language.',
               'default': 3,
            },
            {
               'name': 'remove_source_folder',
               'label': 'Remove source folder',
               'type': 'bool',
               'description': 'Remove source folder on succeed (the one created after the renaming).',
               'default': False,
            },
            {
               'advanced': True,
               'name': 'language_separator',
               'label': 'Languages separator',
               'default': ',',
               'description': ('Separate languages (if many)','Example: ",",".","-" (without quotes).')
            },
         ],
      }
   ],
}]
