# Queuepipe

A demo of making pipelines that act like unix pipelines, ie:

- all processes in the pipeline run in parallel
- input & output is buffered, allowing easy parallelism

Use case:

Say you've got a linear workflow `a -> b -> c`. `a` and `c` are fast local
calculations, but b makes a remote call and has to wait for a response. To speed
things up, you can run multiple instances of b:

```
             --->  b  ---
           /              \
a -> queue ----->  b  -----> queue -> c
           \              /
             --->  b  ---
```

Using this demo:

```py
input, output = make_pipeline([
    a,
    Pipeable(b, parallelism=3),
    c
])

for x in my_input_values: input.put(x)

# you must signal the end of input, otherwise worker threads will run forever
input.put(END)

# optionally get output
while True:
    y = output.get()
    print(y)
    if y is END:
        break
```


Be aware:

- make sure to always put END into the input, otherwise the program will hang
- message ordering is not guaranteed when using parallelism > 1
- multiple return values will be passed to the next function as a list of those
  values, ie. for `return a, b`, the next function will be passed `[a, b]`


# Also see
- [pipe](https://pypi.org/project/pipe/): write `pipelines | like | this` in
  python. Synchronous.
