# shallow-plan
Word2Vec approach for completing plans with missing actions

### Commands

For training and testing

```bash
python train_and_test.py blocks t
```

For testing (using an already saved model)
```bash
python train_and_test.py blocks
```

### Outputs

```bash
$> python train_and_test.py blocks

=== Domain : blocks ===

Training : COMPLETE!
Testing : RUNNING . . .
Testing : COMPLETE!

Total unknown actions: 1436; Total correct predictions: 612
Accuracy: 42.6183844011
```
