import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from tools import register_hooks


def plot_results(
    epochs,
    losses,
    train_accuracies,
    test_accuracies,
    title=None,
):
    """Plot results after training a model."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    ax1.plot(epochs, losses, "o--")
    ax1.set_xlabel("Epoch Number")
    ax1.set_ylabel("Cross Entropy")
    ax1.set_title("Cross Entropy")

    ax2.plot(
        range(len(train_accuracies)), train_accuracies, "o--", label="Training Accuracy"
    )
    ax2.plot(range(len(test_accuracies)), test_accuracies, "o--", label="Test Accuracy")
    ax2.set_xlabel("Epoch number")
    ax2.set_ylabel("Accuracy, in %")
    ax2.set_title("Accuracy")

    plt.legend()
    plt.suptitle(f"{title}", fontsize=28)
    plt.show()


def plot_reg_results(
    epochs,
    losses,
    reg_losses,
    train_accuracies,
    test_accuracies,
    title=None,
):
    """Plot results after training a model with regularization."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    ax1.plot(epochs, losses, "o--", label="Total Loss")
    ax1.plot(epochs, reg_losses, "o--", label="Regularization Loss")
    ax1.plot(
        epochs,
        np.asarray(losses) - np.asarray(reg_losses),
        "o--",
        label="Cross Entropy Loss",
    )
    ax1.set_xlabel("Epoch Number")
    ax1.set_ylabel("Loss")
    ax1.set_title("Losses")

    ax2.plot(
        range(len(train_accuracies)), train_accuracies, "o--", label="Training Accuracy"
    )
    ax2.plot(range(len(test_accuracies)), test_accuracies, "o--", label="Test Accuracy")
    ax2.set_xlabel("Epoch number")
    ax2.set_ylabel("Accuracy, in %")
    ax2.set_title("Accuracy")

    ax1.legend()
    ax2.legend()
    plt.suptitle(f"{title}", fontsize=28)
    plt.show()


def plot_weight_distributions(model, title=None):
    """Plot weight distributions of model."""
    layers_with_weights = [
        (name, module)
        for name, module in model.named_modules()
        if hasattr(module, "weight") and not isinstance(module, nn.CrossEntropyLoss)
    ]

    fig, axs = plt.subplots(
        len(layers_with_weights), 1, figsize=(10, len(layers_with_weights) * 5)
    )
    if len(layers_with_weights) == 1:
        axs = [axs]

    for i, (name, layer) in enumerate(layers_with_weights):
        weights = layer.weight.data.cpu().numpy()
        weights = weights.flatten()
        ax = axs[i]
        sns.histplot(weights, kde=True, ax=ax, bins=30)
        ax.set_title(f"Layer {i+1}: {name} Weight Distribution")

    plt.suptitle(f"{title}", fontsize=24)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # To provide space for the global title
    plt.show()


def plot_activation_maps(model, dataloader, num_images=2):
    """Plots activation maps for each filter in each convolutional layer of model."""

    # Get random batch of images from the dataloader
    data_iter = iter(dataloader)
    images, _ = next(data_iter)

    # Select random subset of images
    indices = torch.randint(0, len(images), (num_images,))
    images = images[indices]

    # Get convolutional layers of model
    conv_layers = [
        module for module in model.modules() if isinstance(module, nn.Conv2d)
    ]

    # Move model to device of images
    device = images.device
    model.to(device)

    # Plot activation maps for each selected image
    for i, image in enumerate(images):
        plt.figure()

        # If the image has more than 1 channel, convert it to grayscale for displaying
        if image.shape[0] > 1:
            image_gray = image.mean(dim=0)
        else:
            image_gray = image[0]

        plt.imshow(image_gray, cmap="gray")
        plt.title(f"Input Image {i + 1}")
        plt.show()

        x = image.unsqueeze(0)  # Add batch dimension

        # Iterate over each convolutional layer
        for j, layer in enumerate(conv_layers):
            x = layer(x)
            x = F.relu(x)  # Apply ReLU activation

            # Plot all activation maps for the current layer
            num_filters = x.shape[1]
            num_cols = int(np.sqrt(num_filters))
            num_rows = num_filters // num_cols + int(num_filters % num_cols != 0)

            fig, axs = plt.subplots(
                num_rows, num_cols, figsize=(num_cols * 3, num_rows * 3)
            )

            for k in range(num_filters):
                row = k // num_cols
                col = k % num_cols
                if num_rows == 1:  # If only 1 row, axs is a 1D array
                    ax = axs[col]
                else:
                    ax = axs[row, col]

                ax.imshow(x[0][k].detach().cpu().numpy(), cmap="gray")
                ax.set_title(f"Filter {k + 1}")
                ax.axis("off")

            fig.suptitle(f"Conv Layer {j + 1} Activation Maps for Image {i + 1}")
            plt.tight_layout()
            plt.show()


def plot_predicted_probabilities(model, data_loader, num_batches=10):
    """
    Compute and plot the model's maximum predicted probability for a number of batches
    from the provided data loader.

    Args:
        model: Trained model.
        data_loader: DataLoader for the data you wish to visualize.
        num_batches: Number of batches to process.
    """
    max_probs = []

    # Ensure we're in evaluation mode
    model.eval()

    with torch.no_grad():
        for i, (data, _) in enumerate(data_loader):
            if i >= num_batches:
                break

            # Compute predicted probabilities
            x = data.to(next(model.parameters()).device)
            y_pred = model(x)

            # Find maximum probability for each sample and store
            max_prob, _ = torch.max(y_pred, dim=1)
            max_probs.extend(max_prob.cpu().numpy())

    # Plot histogram of maximum predicted probabilities
    plt.figure(figsize=(10, 5))
    sns.histplot(max_probs, bins=30, kde=False)
    plt.xlabel("Maximum predicted probability")
    plt.ylabel("Count")
    plt.title("Histogram of maximum predicted probabilities")
    plt.grid(True)
    plt.show()


def plot_activations_pca(model, data_loader, device):
    save_output, hook_handles, layer_names = register_hooks(model)
    model.eval()

    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    with torch.no_grad():
        for images, batch_labels in data_loader:
            images = images.to(device)
            model(images)
            batch_labels = batch_labels.cpu().numpy()
            break

        for i, output in enumerate(save_output.outputs):
            output = output.view(output.size(0), -1).cpu().numpy()

            pca = PCA(n_components=2)
            result = pca.fit_transform(output)

            plt.figure(figsize=(6, 6))
            added_labels = set()
            for j in range(len(result)):
                label = str(int(batch_labels[j]))
                if label not in added_labels:
                    plt.scatter(
                        result[j, 0],
                        result[j, 1],
                        color=colors[int(label)],
                        label=label,
                    )
                    added_labels.add(label)
                else:
                    plt.scatter(result[j, 0], result[j, 1], color=colors[int(label)])

            handles, legend_labels = plt.gca().get_legend_handles_labels()
            by_label = {label: handle for label, handle in zip(legend_labels, handles)}
            ordered_labels = sorted(by_label.keys(), key=int)
            ordered_handles = [by_label[label] for label in ordered_labels]
            plt.legend(ordered_handles, ordered_labels)

            plt.title(f"PCA of {layer_names[i]} Layer")
            plt.show()

    for handle in hook_handles:
        handle.remove()

    save_output.clear()


def plot_activations_tsne(model, data_loader, device):
    save_output, hook_handles, layer_names = register_hooks(model)
    model.eval()

    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    with torch.no_grad():
        for images, batch_labels in data_loader:
            images = images.to(device)
            model(images)
            batch_labels = batch_labels.cpu().numpy()
            break

        for i, output in enumerate(save_output.outputs):
            output = output.view(output.size(0), -1).cpu().numpy()

            tsne = TSNE(n_components=2, random_state=0)
            result = tsne.fit_transform(output)

            plt.figure(figsize=(6, 6))
            added_labels = set()
            for j in range(len(result)):
                label = str(int(batch_labels[j]))
                if label not in added_labels:
                    plt.scatter(
                        result[j, 0],
                        result[j, 1],
                        color=colors[int(label)],
                        label=label,
                    )
                    added_labels.add(label)
                else:
                    plt.scatter(result[j, 0], result[j, 1], color=colors[int(label)])

            handles, legend_labels = plt.gca().get_legend_handles_labels()
            by_label = {label: handle for label, handle in zip(legend_labels, handles)}
            ordered_labels = sorted(by_label.keys(), key=int)
            ordered_handles = [by_label[label] for label in ordered_labels]
            plt.legend(ordered_handles, ordered_labels)

            plt.title(f"t-SNE of {layer_names[i]} Layer")
            plt.show()

    for handle in hook_handles:
        handle.remove()

    save_output.clear()


def plot_saliency_maps(model, data_loader, num_images):
    # Set the model to evaluation mode
    model.eval()

    count = 0

    # Create a grid to plot the images and saliency maps
    rows = int(np.ceil(np.sqrt(num_images)))
    cols = 3
    fig, axs = plt.subplots(rows, cols, figsize=(12, 10))

    for images, labels in data_loader:
        # Enable gradient calculation for the images
        images.requires_grad = True

        # Forward pass
        outputs = model(images)

        # Calculate gradients of the output with respect to the input images
        model.zero_grad()
        batch_size = images.size(0)
        for i in range(batch_size):
            if count >= num_images:
                break

            outputs[i, labels[i]].backward(retain_graph=True)

            # Get the gradients for the i-th image
            gradients = images.grad.data[i]

            # Convert the gradients to grayscale
            grayscale_gradients = torch.mean(gradients, dim=0, keepdim=True)

            # Normalize the gradients between 0 and 1
            normalized_gradients = torch.abs(grayscale_gradients).squeeze()
            normalized_gradients = (
                normalized_gradients - normalized_gradients.min()
            ) / (normalized_gradients.max() - normalized_gradients.min())

            # Convert the normalized gradients to a numpy array
            saliency_map = normalized_gradients.detach().cpu().numpy()

            # Plot the image
            ax_img = axs[count // cols, 0]
            ax_img.imshow(np.transpose(images[i].detach().cpu().numpy(), (1, 2, 0)))
            ax_img.axis("off")

            # Plot the saliency map
            ax_saliency = axs[count // cols, 1]
            ax_saliency.imshow(saliency_map, cmap="hot", alpha=0.5)
            ax_saliency.axis("off")

            # Plot the overlapping image
            ax_overlap = axs[count // cols, 2]
            ax_overlap.imshow(np.transpose(images[i].detach().cpu().numpy(), (1, 2, 0)))
            ax_overlap.imshow(saliency_map, cmap="hot", alpha=0.5)
            ax_overlap.axis("off")

            count += 1

        if count >= num_images:
            break

    # Remove any remaining empty subplots
    for i in range(count, rows * cols):
        axs.flatten()[i].remove()

    # Adjust spacing and display the plot
    plt.tight_layout()
    plt.show()


def plot_occlusion_sensitivity(
    model, data_loader, num_images, occluder_size=8, stride=4
):
    model.eval()

    fig, axs = plt.subplots(num_images, 2, figsize=(10, num_images * 5))

    count = 0
    for images, _ in data_loader:
        for image in images:
            if count >= num_images:
                break

            # Obtain the dimensions of the input image
            image_height, image_width = image.shape[-2:]

            # Calculate the number of occluders that can fit along each dimension
            num_occluders_height = (image_height - occluder_size) // stride + 1
            num_occluders_width = (image_width - occluder_size) // stride + 1

            # Create a grid to store the occlusion scores
            occlusion_scores = np.zeros((num_occluders_height, num_occluders_width))

            # Forward pass through the model to get the predicted class
            output = model(image.unsqueeze(0))
            predicted_class = torch.argmax(output, dim=1).item()

            # Iterate through all occluders and calculate the model's output confidence
            for i in range(num_occluders_height):
                for j in range(num_occluders_width):
                    # Occlude the region of the image with the occluder
                    occluded_image = image.clone()
                    occluded_image[
                        :,
                        i * stride : i * stride + occluder_size,
                        j * stride : j * stride + occluder_size,
                    ] = 0

                    # Forward pass through the model
                    output = model(occluded_image.unsqueeze(0))
                    confidence = F.softmax(output, dim=1)[0, predicted_class].item()

                    # Store the confidence score in the occlusion scores grid
                    occlusion_scores[i, j] = confidence

            # Normalize the occlusion scores between 0 and 1
            occlusion_scores = (occlusion_scores - occlusion_scores.min()) / (
                occlusion_scores.max() - occlusion_scores.min()
            )

            # Plot the original image on the left subplot
            axs[count, 0].imshow(image.permute(1, 2, 0))
            axs[count, 0].axis("off")

            # Plot the occlusion scores heatmap on the right subplot
            heatmap = axs[count, 1].imshow(
                occlusion_scores, cmap="hot", interpolation="nearest"
            )
            axs[count, 1].axis("off")

            # Add a colorbar for the heatmap
            fig.colorbar(heatmap, ax=axs[count, 1])

            count += 1
        if count >= num_images:
            break

    # Show the plot
    plt.tight_layout()
    plt.show()
