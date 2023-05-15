import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from flytekit import task, workflow, Resources
import torch as th
from torch import nn

"""
This example is a simple MNIST training example. It uses the PyTorch framework to train a simple CNN model on the MNIST dataset.
The model is trained for 10 epochs and the validation loss is calculated on the test set.
"""


@task
def get_dataset(training: bool, gpu: bool = False) -> DataLoader:
    """
    This task downloads the MNIST dataset and returns a dataloader for the dataset.
    If GPU is enabled, the dataloader is configured to use the GPU.
    :return: A dataloader for the MNIST dataset.
    """
    dataset = datasets.MNIST("/tmp/mnist", train=training, download=True, transform=transforms.ToTensor())
    if gpu and training is True:
        dataloader = DataLoader(dataset, batch_size=64, shuffle=True, pin_memory_device="cuda", pin_memory=True)
    else:
        dataloader = DataLoader(dataset, batch_size=64, shuffle=True)
    return dataloader


@task(requests=Resources(cpu="2", mem="10Gi"))
def train_model_cpu(model: th.nn.Sequential, optim: th.optim.Optimizer, dataset: DataLoader,
                    n_epochs: int) -> th.nn.Sequential:
    """
    This task trains the model for the specified number of epochs.
    This variant of the task uses the CPU for training. as you can see from the Resources requested in the task decorator.
    """
    return train_model(model=model, optim=optim, dataset=dataset, n_epochs=n_epochs)


@task(requests=Resources(gpu="1", mem="10Gi"))
def train_model_gpu(model: th.nn.Sequential, optim: th.optim.Optimizer, dataset: DataLoader,
                    n_epochs: int) -> th.nn.Sequential:
    """
    This task trains the model for the specified number of epochs.
    This variant of the task uses the GPU for training. as you can see from the Resources requested in the task decorator.
    """
    return train_model(model=model, optim=optim, dataset=dataset, n_epochs=n_epochs)


"""
General Functions, used by Tasks
"""


def get_model_architecture() -> (th.nn.Sequential, th.optim.Optimizer):
    model = nn.Sequential(
        nn.Conv2d(1, 16, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2),
        nn.Conv2d(16, 32, kernel_size=3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2),
        nn.Flatten(),
        nn.Linear(32 * 7 * 7, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )
    optimizer = th.optim.SGD(model.parameters(), lr=0.003, momentum=0.9)
    return model, optimizer


def train_model(model: th.nn.Sequential, optim: th.optim.Optimizer, dataset: DataLoader,
                n_epochs: int) -> th.nn.Sequential:
    """
    This function runs the inner training loop for the specified number of epochs.
    If a GPU is available, the model is moved to the GPU and the training is done on the GPU.
    """
    if th.cuda.is_available():
        model.to("cuda").train()
    else:
        model.train()
    for epoch in range(n_epochs):
        for data, target in dataset:
            if th.cuda.is_available():
                data, target = data.to("cuda"), target.to("cuda")
            optim.zero_grad()
            output = model.forward(data)
            loss = th.nn.functional.nll_loss(output, target)
            loss.backward()
            optim.step()
    return model


@task(requests=Resources(cpu="2", mem="10Gi"))
def validation_loss(model: th.nn.Sequential, dataset: DataLoader) -> str:
    """
    This task calculates the validation loss on the test set.
    This is always run in CPU mode, regardless of the GPU setting. It simply returns the NNL Model Loss on the test set.
    """
    model.to("cpu").eval()
    losses = []
    with torch.no_grad():
        for data, target in dataset:
            data, target = data.to("cpu"), target.to("cpu")
            output = model.forward(data)
            loss = th.nn.functional.nll_loss(output, target)
            losses.append(loss.item())
    loss = 0
    for l in losses:
        loss += l
    loss = loss / len(losses)
    return "NLL model loss in test set: " + str(loss)


@workflow
def mnist_workflow_cpu(n_epoch: int = 10) -> str:
    """Declare workflow called `wf`.
    The @dynamic decorator defines a dynamic workflow.
    Dynamic workflows allow for executing arbitrary python code, and are useful for cases where the
    workflow is not known at compile time.

    This particular workflow is dynamic to enable the user to choose whether to run the training on the GPU or not.
    """
    training_dataset = get_dataset(training=True, gpu=False)
    test_dataset = get_dataset(training=False, gpu=False)
    model, optim = get_model_architecture()
    trained_model = train_model_cpu(model=model, optim=optim, dataset=training_dataset, n_epochs=n_epoch)
    output = validation_loss(model=trained_model, dataset=test_dataset)
    return output

@workflow
def mnist_workflow_gpu(n_epoch: int = 10) -> str:
    training_dataset = get_dataset(training=True, gpu=True)
    test_dataset = get_dataset(training=False, gpu=True)
    model, optim = get_model_architecture()
    trained_model = train_model_gpu(model=model, optim=optim, dataset=training_dataset, n_epochs=n_epoch)
    output = validation_loss(model=trained_model, dataset=test_dataset)
    return output


if __name__ == "__main__":
    # Execute the workflow, simply by invoking it like a function and passing in
    # the necessary parameters
    print(f"Running wf() {mnist_workflow_cpu(n_epoch=10)}")
