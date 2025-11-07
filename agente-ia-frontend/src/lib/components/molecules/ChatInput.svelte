<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    // Props que este componente recibe de la página principal
    export let value: string;
    export let placeholder: string;
    export let disabled: boolean;

    // Creamos un "despachador" de eventos
    const dispatch = createEventDispatcher();

    function handleSubmit() {
        dispatch('submitQuery'); // Enviamos un evento 'submitQuery' a la página padre
    }
</script>

<footer class="input-form">
    <form on:submit|preventDefault={handleSubmit} style="display: contents;">
        <input 
            type="text" 
            {placeholder}  
            bind:value={value} {disabled}
        >
        <button type="submit" {disabled} aria-label="Enviar mensaje">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
        </button>
    </form>
</footer>

<style>
    .input-form {
        display: flex;
        padding: 20px;
        border-top: 1px solid rgb(58, 61, 241)4f588;
        background-color: #e1e1fc59;
        flex-shrink: 0;
    }
    .input-form form {
        display: flex;
        width: 100%;
        gap: 10px;
    }
    .input-form input {
        flex-grow: 1;
        border: none;
        background-color: #F3F4F6;
        padding: 15px 20px;
        border-radius: 30px;
        font-size: 1rem;
        outline-color: #6a5af9;
    }
    .input-form button {
        flex-shrink: 0;
        width: 50px;
        height: 50px;
        border: none;
        background: linear-gradient(120deg, #7D6BFF, #5A4DF8);
        color: white;
        border-radius: 50%;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .input-form button:hover:not(:disabled) {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(90, 77, 248, 0.3);
    }
    .input-form button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    
    /* Estilos para móvil (Responsive) */
    @media (max-width: 768px) {
        .input-form {
            padding: 15px;
        }
        .input-form input {
            padding: 12px 18px;
            font-size: 0.95rem;
        }
        .input-form button {
            width: 45px;
            height: 45px;
        }
    }
</style>