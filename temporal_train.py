"""
Train our temporal-stream CNN on optical flow frames.
"""
from keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger, LearningRateScheduler
from temporal_train_model import ResearchModels
from temporal_train_data import DataSet
import time
import os.path


def fixed_schedule(epoch):
    initial_lr = 1.e-2
    lr = initial_lr

    if epoch == 1389:
        lr = 0.1 * lr
    if epoch == 1944:
        lr = 0.1 * lr

    return lr

def train(num_of_snip=5, opt_flow_len=10, saved_model=None,
        class_limit=None, image_shape=(224, 224),
        load_to_memory=False, batch_size=32, nb_epoch=100):

    # Callbacks: Save the model.
    directory1 = os.path.join('/data/d14122793/two_stream', 'checkpoints')
    checkpointer = ModelCheckpoint(
            filepath=os.path.join(directory1,
                    'Temporal-Training-{epoch:03d}-{val_loss:.3f}.hdf5'),
            verbose=1,
            save_best_only=True)

    # Callbacks: Early stopper.
    early_stopper = EarlyStopping(monitor='loss', patience=200)

    # Callbacks: Save results.
    directory3 = os.path.join('/data/d14122793/two_stream', 'logs')
    timestamp = time.time()
    csv_logger = CSVLogger(os.path.join(directory3, 'training-temporal' + \
            str(timestamp) + '.log'))

    # Learning rate schedule.
    lr_schedule = LearningRateScheduler(fixed_schedule, verbose=0)

    print("class_limit = ", class_limit)
    # Get the data and process it.
    if image_shape is None:
        data = DataSet(
                num_of_snip=num_of_snip,
                opt_flow_len=opt_flow_len,
                class_limit=class_limit
                )
    else:
        data = DataSet(
                num_of_snip=num_of_snip,
                opt_flow_len=opt_flow_len,
                image_shape=image_shape,
                class_limit=class_limit,
                )

    # Get samples per epoch.
    # Multiply by 0.7 to attempt to guess how much of data.data is the train set.
    steps_per_epoch = (len(data.data_list) * 0.7) // batch_size

    if load_to_memory:
        # Get data.
        X, y = data.get_all_stacks_in_memory('train')
        X_test, y_test = data.get_all_stacks_in_memory('test')
    else:
        # Get generators.
        train_generator = data.stack_generator(batch_size, 'train')

        val_generator = data.stack_generator(batch_size, 'test')

    # Get the model.
    temporal_cnn = ResearchModels(nb_classes=len(data.classes), num_of_snip=num_of_snip, opt_flow_len=opt_flow_len,
                                  image_shape=image_shape, saved_model=saved_model)

    # Fit!
    if load_to_memory:
        # Use standard fit.
        temporal_cnn.model.fit(
                X,
                y,
                batch_size=batch_size,
                validation_data=(X_test, y_test),
                verbose=1,
                callbacks=[early_stopper, csv_logger],
                epochs=nb_epoch)
    else:
        # Use fit generator.
        temporal_cnn.model.fit_generator(
                generator=train_generator,
                steps_per_epoch=steps_per_epoch,
                epochs=nb_epoch,
                verbose=1,
                callbacks=[csv_logger, checkpointer, lr_schedule],
                validation_data=val_generator,
                validation_steps=1,
                workers=1,
                use_multiprocessing=False)


def main():
    saved_model = None
    class_limit = 101  # int, can be 1-101 or None
    num_of_snip = 1  # number of chunks used for each video
    opt_flow_len = 10  # number of optical flow frames used
    image_shape = (224, 224)
    load_to_memory = False  # pre-load the sequences into memory
    batch_size = 256
    nb_epoch = 2300

    train(num_of_snip=num_of_snip, opt_flow_len=opt_flow_len, saved_model=saved_model,
          class_limit=class_limit, image_shape=image_shape, load_to_memory=load_to_memory,
          batch_size=batch_size, nb_epoch=nb_epoch)


if __name__ == '__main__':
    main()
