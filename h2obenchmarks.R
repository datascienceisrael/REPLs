################################
# REPL to run benchmark models #
################################

# default values
MAX_CORES <- 14

# auxilliary function
sm <- function(x) suppressMessages(x)
sw <- function(x) suppressWarnings(x)




# libraries ----

# install if necessary
pkgs <- c("dplyr", "ggplot2", "h2o", "readr")
new.packages <- pkgs[!(pkgs %in% installed.packages()[,"Package"])]
if (length(new.packages))
  install.packages(new.packages )

# load all libraries
sm(library(h2o))
sm(library(dplyr))
sm(library(ggplot2))
sm(library(readr))



# init the h2o.cluster ----

cat("\nHow many cores to use? (< 14, integer) : ")

# number of cores to use
inp <- NA
while(is.na(inp)){
  inp <- readLines(file("stdin"), 1)
  inp <- ifelse(grepl("[^0-9.]",inp), NA, as.numeric(inp))
  if(is.na(inp)) cat("\nEnter an integer in [1,14] : ")
}

n_cores  =  if_else(between(inp, 1, 14), inp, MAX_CORES) # user argument, defaults to 14
cat("\nUsing", n_cores, "cores")


# maximum cluster size
cat("\nMaximum cluster size? (e.g. 30G) : ")
size_lim = readLines(file("stdin"),1)



# h2o does his magic -----

# init the cluster 
sw(h2o.init(nthreads = n_cores, max_mem_size = size_lim))

# load the dataset:
cat("\nEnter the full path for .csv data file (/home/user/data/raw/file.csv) : ")

inp <- ""
while(!file.exists(inp)){
  inp <- readLines(file("stdin"), 1)
  if (file.exists(inp)) {
    cat("\nReading file..")
  } else {
    cat("\nFile does not exist\n\tEnter the full file path e.g. /home/user/data/raw/file.csv : ") 
  }
}

# load the dataset into the h2o cluster
df.hex <- h2o.uploadFile(path = inp, 
                         destination_frame = "df.hex",
                         progressBar = TRUE)
cat("\nDataset loaded!")

# name of target variable and prediction type:
cat("\nType of prediction problem? Regression=1, Classification=2; : ")

inp <- NA
sw(
  while(!inp %in%  c(1, 2)){
    inp <- readLines(file("stdin"), 1)
    inp <- ifelse(inp != 1 && inp != 2, NA, as.numeric(inp))
    if(is.na(inp)) cat("\nEnter 1 for regression or 2 for classification: ")
  })


cat("\nTarget variable name: ")
target <- ""

# verify target variable validity:
sw(
  while(!target %in% names(df.hex)) {
    target <- readLines(file("stdin"), 1)
    target <- ifelse(target %in% names(df.hex), as.character(target), NA)
    if(is.na(target)) cat("\ntarget variable name is not in dataset! Re-enter name: ")
  })

cat("\nUsing", target, "as label")


# convert to factor or numeric if necessary:
if (inp == 1) {
  # regression
  cat("\nMaking sure label is numeric...")
  df.hex[target] <- as.numeric(df.hex[target])
  
} else {
  # classification
  cat("\nMaking sure label is categorical...")
  df.hex[target] <- as.factor(as.character(df.hex[target]))
}

# partition to train test and validation
cat("\nDiving dataset to train, validation and test (70/15/15)...")
split_h2o <- h2o.splitFrame(df.hex, c(0.7, 0.15), seed = 1124)

# perform the partition
train_h2o <- h2o.assign(split_h2o[[1]], "train" ) # 70%
valid_h2o <- h2o.assign(split_h2o[[2]], "valid" ) # 15%
test_h2o  <- h2o.assign(split_h2o[[3]], "test" )  # 15%




# Train the Machine Learning model -----
y <- target
x <- setdiff(names(train_h2o), y)

# train the model
cat("\nTraining the model...")
gbm.model <- h2o.gbm(
  x = x,
  y = y,
  training_frame   = train_h2o,
  validation_frame =  valid_h2o,
  seed = 1458
)




# Evaluate the model ----

# Predict on hold-out set, test_h2o
pred_h2o <- h2o.predict(object = gbm.model, newdata = test_h2o)

# performance
cat("\nModel evaluation:\n")
h2o.performance(model = gbm.model, newdata = test_h2o)
cat("\n")

# variable importance
h2o.varimp(object = gbm.model)
h2o.varimp_plot(gbm.model, num_of_features = 5)
cat("\nCheck Rplots.pdf for the variable importance plot")




# shutdown the h2o.cluster -----
cat("\nAll done... shutting down the cluster\n")
h2o.shutdown(prompt = F)

# terminate R session
quit()
