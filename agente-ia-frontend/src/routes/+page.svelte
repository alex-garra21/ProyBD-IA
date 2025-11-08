<script lang="ts">
    // --- 1. Imports ---
    import { onMount } from "svelte";

    // Imports de nuestros nuevos componentes
    import ChatHeader from "$lib/components/organisms/ChatHeader.svelte";
    import ChatHistory from "$lib/components/organisms/ChatHistory.svelte";
    import ChatInput from "$lib/components/molecules/ChatInput.svelte";

    // --- 2. Definición de Tipos (Estado) ---
    interface ConversationState {
        intent?: string;
        table?: string;
        data_collected?: { [key: string]: any };
        missing_fields?: string[];
        last_asked_field?: string;
    }

    const API_URL = "http://127.0.0.1:5000/ask-agent";

    let conversationState: ConversationState = {};
    let userQuery = ""; // El estado del input se queda aquí
    let isLoading = false;

    let chatArea: HTMLDivElement; // Referencia para el scroll

    let conversationHistory: any[] = [
        {
            sender: "agent",
            text: "Hola, soy tu Agente de IA, conectado a la base de datos HR. ¿Cómo puedo ayudarte hoy?",
            type: "status",
        },
    ];
    // --- 3. Lógica de API (Sin cambios) ---
    async function handleUserQuery() {
        if (!userQuery.trim() || isLoading) return;

        const currentQuery = userQuery;
        userQuery = ""; // Limpiamos el input después de enviar
        isLoading = true;

        conversationHistory = [
            ...conversationHistory,
            {
                sender: "user",
                text: currentQuery,
                isResponse: Object.keys(conversationState).length > 0,
            },
        ];

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: currentQuery,
                    conversation_state: conversationState,
                }),
            });

            if (!response.ok) {
                let errorText = `Error HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorText = errorData.agent_text || errorText;
                } catch (e) {
                    /* No se pudo parsear */
                }
                throw new Error(errorText);
            }

            const data = await response.json();
            conversationState = data.conversation_state || {};

            conversationHistory = [
                ...conversationHistory,
                {
                    sender: "agent",
                    text: data.agent_text,
                    sql: data.sql_statement,
                    type: data.type,
                    data: data.data || [],
                },
            ];
        } catch (error: any) {
            console.error("Error al conectar con la API:", error);
            conversationHistory = [
                ...conversationHistory,
                {
                    sender: "agent",
                    text: `⚠️ Lo siento, falló la conexión con el Agente (API). <br><small>${error.message}</small>`,
                    type: "error",
                },
            ];
            conversationState = {};
        } finally {
            isLoading = false;
        }
    }

    // --- 4. Lógica de Interfaz (Sin cambios) ---
    function getPlaceholder() {
        if (
            conversationState &&
            conversationState.missing_fields &&
            conversationState.missing_fields.length > 0
        ) {
            const field = conversationState.missing_fields[0];
            return `Ingresa el valor para el campo: ${field}...`;
        }
        return "Escribe tu solicitud (Ej: 'insertar a...', 'listar empleados...')...";
    }

    $: if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
</script>

<svelte:head>
    <title>Agente IA/SQL (Refactorizado)</title>
</svelte:head>

<div class="chat-container">
    <ChatHeader
        title="🤖 Agente de IA con Base de Datos"
        subtitle="Comunicación con la DB usando Lenguaje Natural"
    />

    <ChatHistory
        history={conversationHistory}
        {isLoading}
        bind:chatAreaElement={chatArea}
    />

    <ChatInput
        bind:value={userQuery}
        placeholder={getPlaceholder()}
        disabled={isLoading}
        on:submitQuery={handleUserQuery}
    />
</div>

<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap");

    :global(body) {
        font-family: "Inter", sans-serif;
        background-color: #e8f0fd;
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        overflow: hidden;
    }

    .chat-container {
        width: 90vw;
        height: 90vh;
        display: flex;
        flex-direction: column;
        background-color: #ffffff;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        box-sizing: border-box;
    }
</style>
