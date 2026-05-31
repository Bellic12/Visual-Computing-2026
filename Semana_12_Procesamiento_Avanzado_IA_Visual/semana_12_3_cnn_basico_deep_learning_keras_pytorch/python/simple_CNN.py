import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.datasets import mnist
from sklearn.metrics import confusion_matrix
import numpy as np
import random

# Cargar el dataset MNIST
(x_train, y_train), (x_test, y_test) = mnist.load_data()

print(f"Número de Imágenes de entrenamiento: {x_train.shape}")


# Mostrar algunas imágenes del dataset
plt.figure(figsize=(10, 10))
for i in range(9):
    plt.subplot(3, 3, i + 1)
    plt.imshow(x_train[i], cmap='gray')
    plt.title(f'Etiqueta: {y_train[i]}')
    plt.axis('off')
plt.tight_layout()
plt.show()

# Normalizar los datos: MNIST son 28x28 en escala de grises (1 canal)
x_train = x_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
x_test = x_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0

print(f"Después del reshape: {x_train.shape}")

# Definir la CNN
simple_CNN = keras.Sequential([
    keras.Input(shape=(28, 28, 1)),                        # Entrada: 28x28 en escala de grises
    layers.Conv2D(32, (3, 3), activation='relu'),          # Capa convolucional con 32 filtros
    layers.MaxPooling2D(),                                 # Pooling para reducir dimensión
    layers.Conv2D(64, (3, 3), activation='relu'),          # Segunda capa convolucional
    layers.MaxPooling2D(),                                 # Pooling
    layers.Flatten(),                                      # Aplanar para capas densas
    layers.Dense(128, activation='relu'),                  # Capa densa oculta
    layers.Dense(10, activation='softmax')                  # Capa de salida: 10 clases (dígitos 0-9)
])

# Compilar el modelo
simple_CNN.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Mostrar la arquitectura del modelo
simple_CNN.summary()

# Entrenar el modelo
history = simple_CNN.fit(
    x_train, y_train,
    epochs=5,
    batch_size=64,
    validation_split=0.2,
    verbose=1
)

# Evaluar en el set de test
test_loss, test_acc = simple_CNN.evaluate(x_test, y_test, verbose=1)
print(f'\nPrecisión en test: {test_acc:.4f}')

# Graficar historial de entrenamiento
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.title('Precisión durante el entrenamiento')
plt.xlabel('Época')
plt.ylabel('Precisión')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Entrenamiento')
plt.plot(history.history['val_loss'], label='Validación')
plt.title('Pérdida durante el entrenamiento')
plt.xlabel('Época')
plt.ylabel('Pérdida')
plt.legend()

plt.tight_layout()
plt.show()

# Matriz de confusión con matplotlib


# Predicciones del modelo
y_pred = simple_CNN.predict(x_test)
y_pred_classes = np.argmax(y_pred, axis=1)

# Calcular matriz de confusión
cm = confusion_matrix(y_test, y_pred_classes)

# Graficar matriz de confusión con matplotlib
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
ax.figure.colorbar(im, ax=ax)

# Configurar etiquetas
ax.set(xticks=np.arange(cm.shape[1]),
       yticks=np.arange(cm.shape[0]),
       xticklabels=range(10), yticklabels=range(10),
       title='Matriz de Confusión',
       ylabel='Etiqueta Real',
       xlabel='Predicción')

# Rotar etiquetas del eje x
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Añadir valores en cada celda
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")

plt.tight_layout()
plt.show()

# Mostrar precisión por clase
print('\nPrecisión por clase:')
for i in range(10):
    true_positives = cm[i, i]
    total_real = cm[i, :].sum()
    precision_class = true_positives / total_real if total_real > 0 else 0
    print(f'  Dígito {i}: {precision_class:.4f} ({true_positives}/{total_real})')


# Detecciones individuales

def mostrar_deteccion(indice):
    plt.imshow(x_test[indice].reshape(28, 28), cmap='gray')
    plt.title(f'Predicción: {y_pred_classes[indice]}, Real: {y_test[indice]}')
    plt.axis('off')
    plt.show()

# Mostrar algunas detecciones individuales
for i in random.sample(range(len(x_test)), 5):
    mostrar_deteccion(i)