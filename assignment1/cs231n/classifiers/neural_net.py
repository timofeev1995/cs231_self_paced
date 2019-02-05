from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt

class TwoLayerNet(object):
    """
  A two-layer fully-connected neural network. The net has an input dimension of
  N, a hidden layer dimension of H, and performs classification over C classes.
  We train the network with a softmax loss function and L2 regularization on the
  weight matrices. The network uses a ReLU nonlinearity after the first fully
  connected layer.

  In other words, the network has the following architecture:

  input - fully connected layer - ReLU - fully connected layer - softmax

  The outputs of the second fully-connected layer are the scores for each class.
    """

    def __init__(self, input_size, hidden_size, output_size, std=1e-4):
        """
        Initialize the model. Weights are initialized to small random values and
        biases are initialized to zero. Weights and biases are stored in the
        variable self.params, which is a dictionary with the following keys:

        W1: First layer weights; has shape (D, H)
        b1: First layer biases; has shape (H,)
        W2: Second layer weights; has shape (H, C)
        b2: Second layer biases; has shape (C,)

        Inputs:
        - input_size: The dimension D of the input data.
        - hidden_size: The number of neurons H in the hidden layer.
        - output_size: The number of classes C.
        """
        self.params = {}
        self.params['W1'] = std * np.random.randn(input_size, hidden_size)
        self.params['b1'] = np.zeros(hidden_size)
        self.params['W2'] = std * np.random.randn(hidden_size, output_size)
        self.params['b2'] = np.zeros(output_size)

    def loss(self, X, y=None, reg=0.0):
        """
        Compute the loss and gradients for a two layer fully connected neural
        network.

        Inputs:
        - X: Input data of shape (N, D). Each X[i] is a training sample.
        - y: Vector of training labels. y[i] is the label for X[i], and each y[i] is
          an integer in the range 0 <= y[i] < C. This parameter is optional; if it
          is not passed then we only return scores, and if it is passed then we
          instead return the loss and gradients.
        - reg: Regularization strength.

        Returns:
        If y is None, return a matrix scores of shape (N, C) where scores[i, c] is
        the score for class c on input X[i].

        If y is not None, instead return a tuple of:
        - loss: Loss (data loss and regularization loss) for this batch of training
          samples.
        - grads: Dictionary mapping parameter names to gradients of those parameters
          with respect to the loss function; has the same keys as self.params.
        """
        # Unpack variables from the params dictionary
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        N, D = X.shape
        num_classes = W2.shape[1]

        # Compute the forward pass
        scores = None
        #############################################################################
        # TODO: Perform the forward pass, computing the class scores for the input. #
        # Store the result in the scores variable, which should be an array of      #
        # shape (N, C).                                                             #
        #############################################################################
        layer1 = np.dot(X, W1) + b1
        layer1_act = layer1 * (layer1 > 0)
        layer2 = np.dot(layer1_act, W2)
        scores = layer2 + b2
        #############################################################################
        #                              END OF YOUR CODE                             #
        #############################################################################

        # If the targets are not given then jump out, we're done
        if y is None:
            return scores

        # Compute the loss
        loss = None
        #############################################################################
        # TODO: Finish the forward pass, and compute the loss. This should include  #
        # both the data loss and L2 regularization for W1 and W2. Store the result  #
        # in the variable loss, which should be a scalar. Use the Softmax           #
        # classifier loss.                                                          #
        #############################################################################
        exp_scores = np.exp(scores - np.max(scores, axis=1, keepdims=True))
        probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
        loss = -np.log(probs * np.eye(len(b2))[y])
        loss = loss[(loss != np.inf) & (loss != -np.inf)]
        loss = np.mean(loss) + reg * (np.sum(W1 * W1) + np.sum(W2 * W2))
        #############################################################################
        #                              END OF YOUR CODE                             #
        #############################################################################

        # Backward pass: compute gradients
        grads = {}
        #############################################################################
        # TODO: Compute the backward pass, computing the derivatives of the weights #
        # and biases. Store the results in the grads dictionary. For example,       #
        # grads['W1'] should store the gradient on W1, and be a matrix of same size #
        #############################################################################
        
        # At first compute classic crossentropy deriviative of output w.r.t. prob output
        output_der = probs - np.eye(num_classes)[y]
        
        # Computation der for b2: output_der is (N x C) we want db2/dL be (C, ), and we 
        # know that partial derivative of b1 is 1 (because of sum operation). Now 
        # we need to sum columns of (N x C) to get (C, ) and after that calculate mean.
        db2 = output_der.mean(axis=0)
        grads['b2'] = db2
        
        # Computation derivative for W2(HxC): its matrix multiplication layer1_act = np.dot(X, W1) + b1 and RELU, 
        # so Z = layer1_act x W2 => dW2/dZ = layer1_act. That means dW2/dL = output_der(NxC) * dW2/dZ = 
        # layer1_act(NxH)_transposed * output_der(NxC), 
        # after this need to derive by n_samples and add regularisation 2 * reg * w
        dW2 = layer1_act.T.dot(output_der)
        dW2 /= N 
        dW2 = dW2 + 2 * reg * W2
        grads['W2'] = dW2
        
        # For computing b1 and W1 derivatives we need to compute derivative of ((W1 x X + b1) x W2 + b2)
        # w.r. to (W1 x X + b1). Its correspond us to W2 and output_der again.
        # Not forget about RELu! Its shape is 
        d_out_to_X2 = output_der.dot(W2.T)
        d_out_to_X2 = d_out_to_X2 * (layer1_act > 0)
        
        # Lets compute b1 derivative. Its gonne be (H, ) shaped
        # After we need to take mean.
        db1 = d_out_to_X2.mean(axis=0)
        grads['b1'] = db1
        
        # And finally derivative of W1
        dW1 = X.T.dot(d_out_to_X2)
        dW1 /= N 
        dW1 += 2 * reg * W1
        grads['W1'] = dW1
        
        #############################################################################
        #                              END OF YOUR CODE                             #
        #############################################################################

        return loss, grads

    def train(self, X, y, X_val, y_val,
            learning_rate=1e-3, learning_rate_decay=0.95,
            reg=5e-6, num_iters=100,
            batch_size=200, verbose=False):
        """
        Train this neural network using stochastic gradient descent.

        Inputs:
        - X: A numpy array of shape (N, D) giving training data.
        - y: A numpy array f shape (N,) giving training labels; y[i] = c means that
          X[i] has label c, where 0 <= c < C.
        - X_val: A numpy array of shape (N_val, D) giving validation data.
        - y_val: A numpy array of shape (N_val,) giving validation labels.
        - learning_rate: Scalar giving learning rate for optimization.
        - learning_rate_decay: Scalar giving factor used to decay the learning rate
          after each epoch.
        - reg: Scalar giving regularization strength.
        - num_iters: Number of steps to take when optimizing.
        - batch_size: Number of training examples to use per step.
        - verbose: boolean; if true print progress during optimization.
        """
        num_train = X.shape[0]
        iterations_per_epoch = max(num_train / batch_size, 1)

        # Use SGD to optimize the parameters in self.model
        loss_history = []
        train_acc_history = []
        val_acc_history = []

        for it in range(num_iters):
          #########################################################################
          # TODO: Create a random minibatch of training data and labels, storing  #
          # them in X_batch and y_batch respectively.                             #
          #########################################################################
            _idx = np.random.choice(X.shape[0], batch_size, replace=False)
            X_batch = X[_idx]
            y_batch = y[_idx]
          #########################################################################
          #                             END OF YOUR CODE                          #
          #########################################################################

          # Compute loss and gradients using the current minibatch
            loss, grads = self.loss(X_batch, y=y_batch, reg=reg)
            loss_history.append(loss)

          #########################################################################
          # TODO: Use the gradients in the grads dictionary to update the         #
          # parameters of the network (stored in the dictionary self.params)      #
          # using stochastic gradient descent. You'll need to use the gradients   #
          # stored in the grads dictionary defined above.                         #
          #########################################################################
            for k, v in self.params.items():
                self.params[k] -= learning_rate * grads[k]
          #########################################################################
          #                             END OF YOUR CODE                          #
          #########################################################################

            if verbose and it % 100 == 0:
                print('iteration %d / %d: loss %f' % (it, num_iters, loss))

          # Every epoch, check train and val accuracy and decay learning rate.
            if it % iterations_per_epoch == 0:
            # Check accuracy
                train_acc = (self.predict(X_batch) == y_batch).mean()
                val_acc = (self.predict(X_val) == y_val).mean()
                train_acc_history.append(train_acc)
                val_acc_history.append(val_acc)

            # Decay learning rate
            learning_rate *= learning_rate_decay

        return {
          'loss_history': loss_history,
          'train_acc_history': train_acc_history,
          'val_acc_history': val_acc_history,
            }

    def predict(self, X):
        """
        Use the trained weights of this two-layer network to predict labels for
        data points. For each data point we predict scores for each of the C
        classes, and assign each data point to the class with the highest score.

        Inputs:
        - X: A numpy array of shape (N, D) giving N D-dimensional data points to
          classify.

        Returns:
        - y_pred: A numpy array of shape (N,) giving predicted labels for each of
          the elements of X. For all i, y_pred[i] = c means that X[i] is predicted
          to have class c, where 0 <= c < C.
        """
        y_pred = None

        ###########################################################################
        # TODO: Implement this function; it should be VERY simple!                #
        ###########################################################################
        scores = self.loss(X)
        y_pred = np.argmax(scores, axis=1)
        ###########################################################################
        #                              END OF YOUR CODE                           #
        ###########################################################################

        return y_pred


