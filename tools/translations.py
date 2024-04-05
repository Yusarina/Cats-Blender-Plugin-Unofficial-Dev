# GPL License

# Thanks to https://www.thegrove3d.com/learn/how-to-translate-a-blender-addon/ for the idea

import os
import csv
import ssl
import bpy
import json
import urllib
import pathlib
import addon_utils
import requests
from bpy.app.translations import locale

from .register import register_wrap
from . import settings

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
settings_file = os.path.join(resources_dir, "settings.json")
translations_dir = os.path.join(resources_dir, "translations")

dictionary: dict[str, str] = dict()
languages = []
verbose = True
translation_download_link = "https://raw.githubusercontent.com/Yusarina/Cats-Blender-Plugin-Unofficial-translations/3.6-4.0-translations/translations.csv"
dictionary_download_link = "https://raw.githubusercontent.com/Yusarina/Cats-Blender-Plugin-Unofficial-translations/3.6-4.0-translations/dictionary.json"

def load_translations():
    global dictionary, languages
    dictionary = dict()
    languages = ["auto"]

    # Check the settings which translation to load
    language = get_language_from_settings()
    # get all current languages
    for i in os.listdir(translations_dir):
        languages.append(i.split(".")[0])
    with open(os.path.join(translations_dir, language+".json"), 'r') as file:
        dictionary = json.load(fp=file)["messages"]
        
    check_missing_translations()


def t(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    output = dictionary.get(phrase)
    if output is None:
        if verbose:
            print('Warning: Unknown phrase: ' + phrase)
        return phrase

    return output.format(*args, **kwargs)


def check_missing_translations():
    for key, value in dictionary.items():
        if not value and verbose:
            print('Translations en_US: Value missing for key: ' + key)


def get_languages_list(self, context):
    choices = []

    for language in languages:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((language, language, language))

    return choices


def update_ui(self, context):
    if settings.update_settings_core(None, None):
        reload_scripts()


def get_language_from_settings():
    # Load settings file
    try:
        with open(settings_file, encoding="utf8") as file:
            settings_data = json.load(file)
    except FileNotFoundError:
        print("SETTINGS FILE NOT FOUND!")
        return
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN SETTINGS FILE")
        return

    if not settings_data:
        print("NO DATA IN SETTINGS FILE")
        return

    lang = settings_data.get("ui_lang")
    if not lang or "auto" in lang.lower():
        return locale

    return lang


def reload_scripts():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == 'Cats Blender Plugin':
            # importlib.reload(mod)
            # bpy.ops.wm.addon_enable(module=mod.__name__)
            # bpy.ops.preferences.addon_disable(module=mod.__name__)
            # bpy.ops.preferences.addon_enable(module=mod.__name__)
            bpy.ops.script.reload()
            break


@register_wrap
class DownloadTranslations(bpy.types.Operator):
    bl_idname = 'cats_translations.download_latest'
    bl_label = 'Download Latest Translations'
    bl_description = 'Download the latest translations for cats UI and internal dictionary'   
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # Download translations.csv from GitHub
        print('DOWNLOAD TRANSLATIONS FILE')
        try:
            response = requests.get(translation_download_link)
            response.raise_for_status()  # Raise an exception if the request was unsuccessful
            with open(translations_file, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.RequestException as e:
            print("TRANSLATIONS FILE COULD NOT BE DOWNLOADED")
            self.report({'ERROR'}, "TRANSLATIONS FILE COULD NOT BE DOWNLOADED: " + str(e))
            return {'CANCELLED'}
        print('TRANSLATIONS DOWNLOAD FINISHED')

        # Download dictionary.json from GitHub
        print('DOWNLOAD DICTIONARY FILE')
        try:
            response = requests.get(dictionary_download_link)
            response.raise_for_status()  # Raise an exception if the request was unsuccessful
            with open(dictionary_file, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.RequestException as e:
            print("DICTIONARY FILE COULD NOT BE DOWNLOADED")
            self.report({'ERROR'}, "DICTIONARY FILE COULD NOT BE DOWNLOADED: " + str(e))
            return {'CANCELLED'}
        print('DICTIONARY DOWNLOAD FINISHED')

        reload_scripts()

        self.report({'INFO'}, "Successfully downloaded the translations and dictionary")
        return {'FINISHED'}


load_translations()
