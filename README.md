# Regularization of Neural Networks
Project: Exploring soft and hard constraints in artificial neural networks.

The folders *Start training*, *UMI*, *UMI RNN* and *JAX* contains testing of regularization on a simple toy problem, and learning how to use pytorch and build/train NNs.

The folder *Regularization benchmarking* contains the actual project with comparison of regularization techniques. I use the network LeNet, and the datasets MNIST, CIFAR10 and CIFAR100 to do the testing. I test how the regularization techniques perform on test data, and visualize parts of the NN to investigate the effect of regularization.

## Overview of Regularization Methods
(With help from ChatGPT)

#### Comparison - No Regularization
In the absence of any regularization, a model simply minimizes the loss function on the training data. This can lead to overfitting, especially in high-dimensional models with many parameters, because the model becomes too complex and learns to fit the training data too closely, including its noise. As a result, it often performs poorly on unseen data. Regularization methods are therefore used to prevent overfitting by adding constraints to the learning process.  

#### L1 Regularization
L1 regularization, also known as Lasso regularization, involves adding a term to the loss function that penalizes the absolute value of the weights. This encourages the model to have sparse weights, meaning that many weights are zero. This can lead to a model that is easier to interpret, because it effectively performs feature selection, choosing a subset of the input features to focus on.  

#### L2 Regularization
L2 regularization, also known as Ridge regularization, involves adding a term to the loss function that penalizes the square of the weights. This encourages the model to have small weights but does not encourage sparsity. L2 regularization can help prevent overfitting by discouraging the model from relying too much on any single input feature.  

#### Elastic Net Regularization
Elastic Net regularization is a compromise between L1 and L2 regularization. It involves adding a term to the loss function that is a mix of an L1 penalty and an L2 penalty. This allows the model to have some level of sparsity, like L1 regularization, while also encouraging small weights, like L2 regularization.  

#### Soft SVB Regularization
Soft SVB regularization, introduced by Jia et al. 2019, penalizes the model based on the Frobenius norm of the difference between the weights' Gram matrix and the identity matrix. This encourages the model's weights to be orthogonal, which can improve generalization. Soft SVB regularization might introduce additional computational cost due to the need to compute matrix multiplications and norms.  

#### Hard SVB Regularization
Hard SVB regularization, similar to Soft SVB, also encourages the model's weights to be orthogonal, but it does so in a more strict manner. It uses a hard constraint instead of a soft penalty, meaning that the model's weights are forced to be orthogonal.  

#### Jacobi Regularization
Jacobi regularization introduces a penalty on the norm of the Jacobian matrix of the model's outputs with respect to its inputs. The Jacobian matrix represents the first-order derivatives of the model. By penalizing the norm of the Jacobian, we encourage the model to have outputs that change linearly or sub-linearly with respect to small changes in the inputs. It can help in achieving more stable models with smoother decision boundaries. However, calculating the Jacobian matrix can be computationally expensive for complex models and large inputs.  

#### Jacobi Determinant Regularization
Jacobi Determinant regularization involves adding a term to the loss function that penalizes the squared difference between the determinant of the Jacobian of the model's outputs with respect to its inputs and one. This regularization approach encourages the model to maintain volume preservation in the input space to the output space. This approach can help the model to learn more balanced and well-distributed representations, which can be beneficial for tasks that involve transformations. However, the computation of the determinant of the Jacobian can be highly computationally expensive, especially for high-dimensional inputs.  

#### Dropout Regularization
Dropout is a popular regularization technique for neural networks. During training, dropout randomly sets a fraction of input units to 0 at each update, which helps to prevent overfitting. This introduces noise into the training process that forces the learning algorithm to learn more robust features that are useful in conjunction with many different random subsets of the other neurons. Dropout can provide a significant improvement in performance, especially for larger neural networks and datasets. However, it may increase the time needed for convergence during training, and it's less interpretable compared to L1 and L2 regularization methods.    

#### Confidence Penalty Regularization
Confidence penalty regularization adds a penalty to the loss function based on the confidence of the model's predictions. If the model is too confident, it is penalized more heavily. This can encourage the model to be more cautious in its predictions, potentially leading to better calibration and more reliable uncertainty estimates. However, this approach may be inappropriate for certain tasks where high confidence is desirable, and it can also make the optimization problem more challenging.   

#### Label Smoothing Regularization
Label Smoothing is a form of regularization where the target labels for a classification problem are replaced with smoothed versions. Instead of having a hard one-hot encoded target, each target will have a small value for each incorrect class and the rest of the value for the correct class. This encourages the model to be less confident, reducing the risk of overfitting and improving generalization.  

#### Hessian Regularization (Not working)
Hessian regularization involves adding a term to the loss function that penalizes the Frobenius norm of the Hessian of the model's outputs with respect to its inputs. The Hessian is a matrix that describes the second-order derivatives of the model. Penalizing the norm of the Hessian encourages the model to have outputs that change linearly or sub-linearly with respect to small changes in the inputs. This can help prevent overfitting by discouraging the model from fitting the training data too closely. However, like with Jacobi regularization, calculating the Hessian matrix can be computationally expensive for complex models.  

#### Noise Injection to Inputs
Noise injection to inputs is a regularization technique where random noise is added to the inputs during training. This encourages the model to be robust to small changes in the inputs. This form of regularization can help prevent overfitting by discouraging the model from fitting the noise in the training data, instead focusing on the underlying patterns that are consistent even when noise is added. However, care must be taken to ensure that the noise does not overpower the signal in the data, as this could lead to the model learning less useful representations.  

#### Noise Injection to Weights
Similar to noise injection to inputs, noise injection to weights involves adding random noise to the weights during training. This can be seen as a form of stochastic regularization, as it adds a source of randomness that the model needs to be robust to. By preventing the weights from settling into a fixed value, it encourages the model to explore different parts of the weight space, which can help it avoid overfitting to the training data. However, like with injecting noise to inputs, care must be taken to ensure that the noise does not overpower the learning signal. Moreover, this method can make the optimization process more challenging and may increase the time required for training.   


## Overview of Visualization Techniques
(With help from ChatGPT)

#### Training and Test Loss Curves
The most straightforward way to visualize the effect of regularization is by plotting the training and validation loss over time. If regularization is working correctly, you should observe a decrease in the gap between training and validation loss, indicating a reduction in overfitting.

#### Weight Distributions
For L1, L2, and Elastic Net regularization, you can visualize the distribution of the weights in the model. L1 regularization should result in many weights being exactly zero, while L2 regularization will typically result in a distribution with smaller magnitudes.

#### Feature Map Visualizations
Especially in the context of convolutional neural networks (CNNs), visualizing the feature maps - the activations of the convolutional layers - can provide insight into what features the network is learning. This can give you a sense of how regularization is affecting the types of features learned. For instance, too much L1/L2 regularization might result in overly simplistic feature maps, while too little might result in feature maps that are overly complex or noisy.

#### Uncertainty Estimates
For regularization methods that affect the model's confidence, like Confidence Penalty and Label Smoothing, you can plot the model's predicted probabilities. A well-regularized model should show less overconfidence and better-calibrated probabilities.

#### T-SNE or PCA of Activations
You can use dimensionality reduction techniques like t-SNE or PCA to visualize the activations of your network, which can be insightful especially for dropout and noise injection techniques. This involves taking the activation values of a particular layer and reducing them to 2 or 3 dimensions for plotting. Different classes should ideally form distinct clusters, and overfitting may manifest as overly complex boundaries between classes.

#### Saliency Maps
A saliency map is a simple, yet effective method for understanding which parts of the image contribute most significantly to a neural network's decision. It is created by calculating the gradient of the output category with respect to the input image. This gradient is then visualized as a heatmap overlaying the original image, with high-gradient regions indicating important areas for the model's decision. The intuition behind this is that the gradient measures how much a small change in each pixel's intensity would affect the final prediction. So, large gradient values suggest important pixels.

#### Occlusion Sensitivity 
Occlusion sensitivity is a method that involves systematically occluding different parts of the input image with a grey square (or other "occluder"), and monitoring the effect on the classifier's output. The output is then visualized as a heatmap showing how much the classifier's confidence decreased when each region was occluded, highlighting important regions in the input image for the model's decision.


### Not implemented
#### Gradient and Hessian Matrices
For gradient and Hessian based regularizations, you can visualize these matrices or their norms. Changes in these matrices can provide insights into how these regularization methods affect the model's sensitivity to changes in the input features.

#### Model Complexity Graphs
You can also plot graphs showing model complexity (like the number of non-zero weights or the norm of the weights) against model performance (like accuracy or AUC-ROC). This can show how the regularization method is affecting the model's complexity and performance.

#### Parameter Trajectory Plots
Parameter trajectory plots visualize the path that the parameters of the model take during training. This is especially useful for understanding the effect of regularization techniques that impact the optimization process directly such as L1, L2, Elastic Net, and noise injection to weights. For each weight in the model, plot its value on the y-axis and the training iteration number (or epoch number) on the x-axis. Note that this could be difficult to interpret for models with a high number of parameters, so it might be best to select a subset of weights or aggregate the weights in some way (e.g., their mean or median).

#### Sensitivity and Robustness Analysis
Another way to visualize the impact of regularization is through sensitivity and robustness analysis. This involves slightly perturbing the input data and measuring how much the model's predictions change. A well-regularized model should be more robust to these perturbations. You can visualize this by plotting the magnitude of the perturbation (x-axis) against the change in model output (y-axis) for different regularization techniques.

#### Training Dynamics Plots
Regularization methods like L1, L2, and Elastic Net affect the learning dynamics of the model. One way to visualize this is to plot the training loss for each mini-batch, rather than each epoch, which can reveal more fine-grained patterns in the learning dynamics. In particular, you might observe more fluctuation in the mini-batch loss when using a regularization method that adds noise (like dropout or noise injection), compared to a method that primarily shrinks the weights (like L1 or L2).

#### Loss Landscape Visualization
This is an advanced visualization technique that plots the loss function as a landscape or surface plot. Regularization can significantly impact the shape of this landscape, potentially making it smoother and more convex, which can make optimization easier. However, these visualizations can be computationally intensive to create and may require sophisticated techniques to interpret.

#### Grad-CAM (Gradient-weighted Class Activation Mapping)
Grad-CAM is an extension of the CAM technique, which allows us to visualize the important regions in the image for a specific prediction. Grad-CAM uses the gradient information flowing into the last convolutional layer of the CNN to understand each neuron’s importance. The gradients are global-average-pooled to obtain the neuron importance weights, and a weighted combination of activation maps is used to compute the Grad-CAM heatmap. This heatmap indicates important regions in the image for a given target class.
