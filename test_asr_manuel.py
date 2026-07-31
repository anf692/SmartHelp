# test_asr_manuel.py
from services.asr_service import transcrire_audio

texte = transcrire_audio("Rufisque.wav")
print("Texte transcrit :", texte)

