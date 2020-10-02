import tensorflow as tf
from environment import Environment
from agent import Agent


if __name__ == '__main__':

    # create environment object
    env = Environment()

    memory_fp = '/path/to/your/memory'
    save_path = '/model/model-weights'

    mem_length = 100000

    agent = Agent(env,
                  tf.keras.optimizers.Adam(learning_rate=0.0001),
                  loss='mse',
                  memory_length=mem_length,
                  dueling=True,
                  noisy_net=True,
                  egreedy=True,
                  save_memory=memory_fp,
                  save_weights=save_path,
                  verbose_action=True)

    #agent.load_weights(save_path)
    #agent.load_memory(memory_fp)
    agent.set_beta_schedule(beta_start=0.4, beta_max=1, annealed_samplings=10000)
    agent.set_epsilon_decay_schedule(1, 0.00001, 10000)

    agent.pretraining_steps = 10000
    print(f'pretraining for {agent.pretraining_steps} steps...')

    env.init_game()

    for episode in range(10000000):
        env.run(episode, agent, batch_size=32, log_fn=None)
