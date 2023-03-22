import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from flytekit import task, dynamic, Resources
import torch as th
from torch import nn

@task
def get_dataset(training: bool, gpu: bool = False) -> DataLoader:
    print("GPU Enabled: " + str(gpu))
    dataset = datasets.MNIST("/tmp/mnist", train=training, download=True, transform=transforms.ToTensor())
    if gpu:
        dataloader = DataLoader(dataset, batch_size=64, shuffle=True, pin_memory_device="cuda", pin_memory=True)
    else:
        dataloader = DataLoader(dataset, batch_size=64, shuffle=True)
    return dataloader


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

@task(requests=Resources(cpu="2", mem="10Gi"))
def train_model_cpu(model: th.nn.Sequential, optim: th.optim.Optimizer,  dataset: DataLoader, n_epochs: int) -> th.nn.Sequential:
    return train_model(model=model, optim=optim, dataset=dataset, n_epochs=n_epochs)

@task(requests=Resources(gpu="1", mem="10Gi"))
def train_model_gpu(model: th.nn.Sequential, optim: th.optim.Optimizer,  dataset: DataLoader, n_epochs: int) -> th.nn.Sequential:
    return train_model(model=model, optim=optim, dataset=dataset, n_epochs=n_epochs)


def train_model(model: th.nn.Sequential, optim: th.optim.Optimizer,  dataset: DataLoader, n_epochs: int) -> th.nn.Sequential:
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



@dynamic
def train_mnist_model(n_epoch: int = 10, gpu_enabled: bool =False) -> str:
    training_dataset = get_dataset(training=True, gpu=gpu_enabled)
    test_dataset = get_dataset(training=False, gpu=gpu_enabled)
    model, optim = get_model_architecture()
    if gpu_enabled:
        trained_model = train_model_gpu(model=model, optim=optim, dataset=training_dataset, n_epochs=n_epoch)
    else:
        trained_model = train_model_cpu(model=model, optim=optim, dataset=training_dataset, n_epochs=n_epoch)
    output = validation_loss(model=trained_model, dataset=test_dataset)
    return output