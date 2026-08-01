from services.vision_service import analyser_image

with open("image1.png", "rb") as fichier:
    bytes_image = fichier.read()

resultat = analyser_image(bytes_image)
print("Diagnostic image :", resultat)

