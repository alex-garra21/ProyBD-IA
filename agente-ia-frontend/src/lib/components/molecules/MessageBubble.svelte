<script lang="ts">
    import { fly } from 'svelte/transition';
    // Recibimos el objeto 'message' como una propiedad (prop)
    export let message: any;
</script>

<div 
    class="message-wrapper {message.sender}"
    in:fly={{ y: 10, duration: 250 }}
>
    <div class={`message ${message.sender} ${message.type === 'error' ? 'error' : ''}`}>
        <p>
            {@html message.text}
        </p>

        {#if message.sql}
            <div class="sql-box">
                <h4>Sentencia SQL Utilizada:</h4>
                <pre>{message.sql}</pre>
            </div>
        {/if}

        {#if message.data && message.data.length > 0}
            <h4>Resultados encontrados:</h4>
            <table>
                <thead>
                    <tr>
                        {#each Object.keys(message.data[0]) as header}
                            <th>{header.toUpperCase()}</th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    {#each message.data as row}
                        <tr>
                            {#each Object.values(row) as value}
                                <td>{value}</td>
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </table>
        {/if}
    </div>
</div>

<style>
    .message-wrapper {
        display: flex;
        max-width: 75%;
    }
    .message-wrapper.user {
        align-self: flex-end;
    }
    .message-wrapper.agent {
        align-self: flex-start;
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

    .message.agent {
        background-color: #F3F4F6;
        color: #333;
        border-bottom-left-radius: 5px;
    }

    .message.user {
        background: linear-gradient(120deg, #7D6BFF, #5A4DF8);
        color: white;
        border-bottom-right-radius: 5px;
    }

    .message.error {
        background-color: #ffe0e0;
        border: 1px solid #ffb0b0;
        border-left: 5px solid red;
        color: #333;
    }

    .sql-box {
        margin-top: 10px;
        padding: 10px;
        background-color: rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        overflow-x: auto;
    }
    .message.agent .sql-box {
        background-color: rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
    .sql-box h4 {
        margin: 0 0 5px 0;
        font-size: 0.8rem;
        font-weight: 600;
        opacity: 0.7;
    }
    pre {
        white-space: pre-wrap;
        word-break: break-all;
        font-family: monospace;
        margin: 0;
        font-size: 0.9em;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        font-size: 0.9em;
    }
    th, td {
        border: 1px solid rgba(0, 0, 0, 0.1);
        padding: 8px 10px;
        text-align: left;
    }
    th {
        background-color: rgba(0, 0, 0, 0.03);
    }
</style>