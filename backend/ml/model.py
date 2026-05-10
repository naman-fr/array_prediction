import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def build_mlp_model(input_shape=(1,)):
    inputs = keras.Input(shape=input_shape, name="target_error_input")

    x = layers.Dense(64, name="dense_1")(inputs)
    x = layers.BatchNormalization(name="bn_1")(x)
    x = layers.Activation("relu", name="relu_1")(x)
    x = layers.Dropout(0.2, name="dropout_1")(x)

    x = layers.Dense(64, name="dense_2")(x)
    x = layers.BatchNormalization(name="bn_2")(x)
    x = layers.Activation("relu", name="relu_2")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)

    x = layers.Dense(32, name="dense_3")(x)
    x = layers.BatchNormalization(name="bn_3")(x)
    x = layers.Activation("relu", name="relu_3")(x)
    x = layers.Dropout(0.2, name="dropout_3")(x)

    outputs = layers.Dense(3, activation="softplus", name="spacings_output")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="SpacingPredictorMLP")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="mse",
        metrics=["mae"]
    )
    return model

def train_model(X_train, Y_train, model_path="spacing_predictor.h5", batch_size=32, epochs=200, validation_split=0.1):
    model = build_mlp_model(input_shape=(1,))

    early_stop = keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=15, restore_best_weights=True
    )

    history = model.fit(
        X_train,
        Y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_split=validation_split,
        callbacks=[early_stop],
        verbose=2
    )

    model.save(model_path)
    print(f"Model saved to '{model_path}'")
    return model

def load_model(model_path="spacing_predictor.h5"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_path}' not found.")
    model = keras.models.load_model(model_path, compile=False)
    return model
