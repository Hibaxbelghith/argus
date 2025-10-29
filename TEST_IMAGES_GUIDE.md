# 🧪 Images de Test pour Détection d'Objets + SMS

## 🔴 OBJETS SUSPECTS (Envoi SMS automatique)

### Couteaux / Knives
1. https://images.pexels.com/photos/4226805/pexels-photo-4226805.jpeg
2. https://images.unsplash.com/photo-1593618998160-e34014e67546
3. https://images.pexels.com/photos/4226878/pexels-photo-4226878.jpeg

### Ciseaux / Scissors
1. https://images.pexels.com/photos/4226257/pexels-photo-4226257.jpeg
2. https://images.unsplash.com/photo-1589998059171-988d887df646
3. https://images.pexels.com/photos/3738386/pexels-photo-3738386.jpeg

### Outils / Tools (peuvent être suspects)
1. https://images.pexels.com/photos/1305095/pexels-photo-1305095.jpeg (marteau)
2. https://images.pexels.com/photos/1078884/pexels-photo-1078884.jpeg (tournevis)

## 🟢 OBJETS NORMAUX (Pas de SMS)

### Personnes
1. https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg
2. https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg

### Animaux
1. https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg (chien)
2. https://images.pexels.com/photos/104827/cat-pet-animal-domestic-104827.jpeg (chat)

### Véhicules
1. https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg (voiture)
2. https://images.pexels.com/photos/100650/pexels-photo-100650.jpeg (moto)

### Objets du quotidien
1. https://images.pexels.com/photos/4226924/pexels-photo-4226924.jpeg (téléphone)
2. https://images.pexels.com/photos/459654/pexels-photo-459654.jpeg (ordinateur)

## 📋 Instructions de Test

### Étape 1 : Télécharger une image
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "https://images.pexels.com/photos/4226805/pexels-photo-4226805.jpeg" -OutFile "knife_test.jpg"
```

### Étape 2 : Uploader sur Argus
1. Ouvrez http://127.0.0.1:8000/detection/
2. Cliquez "Choose File"
3. Sélectionnez l'image téléchargée
4. Cliquez "Detect Objects"

### Étape 3 : Vérifier le résultat
- ✅ Objet détecté
- 📊 Analytics mis à jour
- ⚠️ Alerte de sécurité créée (si objet suspect)
- 📱 **SMS envoyé** (si objet suspect ET sévérité >= medium)

## 🎯 Tests Recommandés

### Test 1 : Couteau (SMS attendu ✅)
```
Image : knife_test.jpg
Objet attendu : knife
Alerte : OUI (suspicious_object)
Sévérité : HIGH
SMS : OUI 📱
```

### Test 2 : Personne (Pas de SMS ❌)
```
Image : person_test.jpg
Objet attendu : person
Alerte : NON
Sévérité : N/A
SMS : NON
```

### Test 3 : Ciseaux (SMS attendu ✅)
```
Image : scissors_test.jpg
Objet attendu : scissors
Alerte : OUI (suspicious_object)
Sévérité : MEDIUM
SMS : OUI 📱
```

## ⚙️ Configuration Actuelle

Votre configuration SMS :
- ✅ Numéro : +21627326154
- ✅ Méthodes activées : web, email, sms
- ✅ Sévérité min SMS : medium
- ✅ Twilio configuré

## 🔍 Liste Complète des Objets YOLO

### Objets SUSPECTS (SMS automatique) :
- knife ✅
- scissors ✅
- fork (selon contexte)
- bottle (selon contexte)
- wine glass (selon contexte)

### Objets NORMAUX (pas de SMS) :
- person
- bicycle
- car, motorcycle, bus, truck
- cat, dog, bird, horse
- chair, couch, bed, table
- laptop, mouse, keyboard, cell phone
- book, clock, vase

### Tous les objets YOLO v5 (80 classes) :
```
person, bicycle, car, motorcycle, airplane, bus, train, truck, boat,
traffic light, fire hydrant, stop sign, parking meter, bench, bird,
cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack,
umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball,
kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket,
bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple,
sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair,
couch, potted plant, bed, dining table, toilet, tv, laptop, mouse,
remote, keyboard, cell phone, microwave, oven, toaster, sink,
refrigerator, book, clock, vase, scissors, teddy bear, hair drier,
toothbrush
```

## 💡 Astuce : Test Rapide

Créez un dossier avec quelques images :
```powershell
# Télécharger plusieurs images de test
mkdir test_images
cd test_images

# Couteau (SMS ✅)
Invoke-WebRequest "https://images.pexels.com/photos/4226805/pexels-photo-4226805.jpeg" -OutFile "1_knife.jpg"

# Ciseaux (SMS ✅)
Invoke-WebRequest "https://images.pexels.com/photos/4226257/pexels-photo-4226257.jpeg" -OutFile "2_scissors.jpg"

# Personne (Pas SMS ❌)
Invoke-WebRequest "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg" -OutFile "3_person.jpg"

# Chien (Pas SMS ❌)
Invoke-WebRequest "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg" -OutFile "4_dog.jpg"
```

Puis testez-les une par une sur http://127.0.0.1:8000/detection/

## 📱 Résultat Attendu

Pour les images avec **knife** ou **scissors** :
1. ✅ Détection réussie
2. ⚠️ Alerte de sécurité créée
3. 📧 Notification web créée
4. 📱 **SMS ENVOYÉ à +21627326154**
5. 💾 Analytics enregistrées

Pour les images normales :
1. ✅ Détection réussie
2. ❌ Pas d'alerte
3. ❌ Pas de SMS
4. 💾 Analytics enregistrées uniquement
