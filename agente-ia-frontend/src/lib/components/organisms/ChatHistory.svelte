<script lang="ts">
    import MessageBubble from '$lib/components/molecules/MessageBubble.svelte';
    
    export let history: any[];
    export let isLoading: boolean;
    
    // Referencia al área de chat para el scroll
    export let chatAreaElement: HTMLDivElement;
</script>

<div class="chat-area" bind:this={chatAreaElement}>
    {#each history as message, i (i)}
        <MessageBubble {message} />
    {/each}

    {#if isLoading}
        <div class="message-wrapper agent">
            <div class="message agent loading">
                <p>Agente: Procesando...</p>
            </div>
        </div>
    {/if}
</div>

<style>
    .chat-area {
        flex-grow: 1;
        overflow-y: auto;
        padding: 25px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    /* Estilos de la burbuja "loading", ya que es específica de este organismo */
    .message.loading {
        background-color: #F3F4F6;
        color: #333;
        border-bottom-left-radius: 5px;
    }
    .message-wrapper.agent {
        align-self: flex-start;
        max-width: 75%;
    }
    .message {
        padding: 12px 18px;
        border-radius: 20px;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    .message p {
        margin: 0;
    }
    
    @media (max-width: 768px) {
        .chat-area {
            padding: 15px;
        }
    }
</style>