import os
import openai
from dotenv import load_dotenv
from flask import Flask, request, send_file
from google.cloud import texttospeech
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

load_dotenv(verbose=True)

OPENAI_KEY = os.getenv("OPENAI_KEY")

app = Flask(__name__)
api = Api(app)

class Translate(Resource):
    def post(self):
        audio_file = request.files['file']
        secure_file = secure_filename(audio_file.filename)
        audio_file.save("data/" + secure_file)
        
        af = open("data/" + secure_file, "rb")
        transcript = openai.Audio.translate("whisper-1", af, api_key=OPENAI_KEY)

        self.text_to_speech(transcript.text, "english.mp3")

        return send_file('english.mp3', as_attachment=True)

    def text_to_speech(self, text, output_filename, language_code='en-US' ):
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )

        with open(output_filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to "{output_filename}"')

api.add_resource(Translate, '/translate')

if __name__ == '__main__':
    app.run(debug=True)