"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
from azureml.core import Model, Run
import argparse


# Get workspace
run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace


parser = argparse.ArgumentParser("evaluate")
parser.add_argument(
    "--build_id",
    type=str,
    help="The ID of the build triggering this pipeline run",
)
parser.add_argument(
    "--model_name",
    type=str,
    help="Name of the Model",
    default="azure_service_classifier",
)
args = parser.parse_args()

print("Argument 1: %s" % args.build_id)
print("Argument 2: %s" % args.model_name)
model_name = args.model_name
build_id = args.build_id

all_runs = exp.get_runs(include_children=True)

# get the last completed run
while True:
    new_model_run = next(all_runs)
    if (new_model_run.get_status() == 'Completed'):
        break
    new_model_run_id = new_model_run.id

# print(f'New Run found with Run ID of: {new_model_run_id}')

model_list = Model.list(ws)

if len(model_list) != 0:  # there are some models
    # # Get most recently registered model, we assume that
    # is the model in production.
    # Download this model and compare it with the recently
    # trained model by running test with same data set.
    # production_model = next(
    #     filter(
    #         lambda x: x.created_time == max(
    #             model.created_time for model in model_list),
    #         model_list,
    #     )
    # )
    # production_model_run_id = production_model.id
    # run_list = exp.get_runs()

    # # Get the run history for both production model and
    # # newly trained model and compare mse
    # production_model_run = production_model.run
    # # new_model_run = Run(exp, run_id=new_model_run_id)

    # production_model_acc = production_model_run.get_metrics().get(
    #     "val_accuracy")
    # new_model_acc = new_model_run.get_metrics().get(
    #     "val_accuracy")
    # print(
    #     "Current Production model acc: {}, New trained model acc: {}".format(
    #         production_model_acc, new_model_acc
    #     )
    # )

    # promote_new_model = False
    # if new_model_acc > production_model_acc:
    #     promote_new_model = True
    #     print("New trained model performs better, will be registered")
    promote_new_model = True
else:
    promote_new_model = True
    print("This is the first model to be trained, \
          thus nothing to evaluate for now")


# Writing the run id to /aml_config/run_id.json
if promote_new_model:
    model_path = './outputs/exports'
    new_model_run.register_model(
        model_name=model_name,
        model_path=model_path,
        properties={"build_id": build_id, "run_type": "train"})
    print("Registered new model!")