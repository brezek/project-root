import { memo, useCallback, useState, useEffect } from 'react'; // Add useState
import { useRecoilValue } from 'recoil';
import { useForm } from 'react-hook-form';
import { useParams } from 'react-router-dom';
import { useGetMessagesByConvoId } from 'librechat-data-provider/react-query';
import type { TMessage } from 'librechat-data-provider';
import type { ChatFormValues } from '~/common';
import { ChatContext, AddedChatContext, useFileMapContext, ChatFormProvider } from '~/Providers';
import { useChatHelpers, useAddedResponse, useSSE } from '~/hooks';
import MessagesView from './Messages/MessagesView';
import { Spinner } from '~/components/svg';
import Presentation from './Presentation';
import ChatForm from './Input/ChatForm';
import { buildTree } from '~/utils';
import Landing from './Landing';
import Header from './Header';
import Footer from './Footer';
import store from '~/store';

// Add Project Selection Component
const ProjectSelector = ({ onSelect }: { onSelect: (id: string) => void }) => {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    // Fetch projects from your FastAPI backend
    const fetchProjects = async () => {
      try {
        const response = await fetch('http://localhost:8000/get_projects/');
        const data = await response.json();
        setProjects(data.projects);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };
    fetchProjects();
  }, []);

  return (
    <select 
      onChange={(e) => onSelect(e.target.value)}
      className="rounded border p-2 dark:bg-gray-800 dark:border-gray-600"
    >
      <option value="">Select Project</option>
      {projects.map((project) => (
        <option key={project.id} value={project.id}>
          {project.name}
        </option>
      ))}
    </select>
  );
};

function ChatView({ index = 0 }: { index?: number }) {
  const { conversationId } = useParams();
  const [currentProjectId, setCurrentProjectId] = useState<string>('');
  const rootSubmission = useRecoilValue(store.submissionByIndex(index));
  const addedSubmission = useRecoilValue(store.submissionByIndex(index + 1));

  const fileMap = useFileMapContext();

  const { data: messagesTree = null, isLoading } = useGetMessagesByConvoId(conversationId ?? '', {
    select: useCallback(
      (data: TMessage[]) => {
        const dataTree = buildTree({ messages: data, fileMap });
        return dataTree?.length === 0 ? null : (dataTree ?? null);
      },
      [fileMap],
    ),
    enabled: !!fileMap,
  });

  // Modify chatHelpers to include project ID in headers
  const chatHelpers = useChatHelpers(index, conversationId);
  const originalSubmit = chatHelpers.handleSubmit;
  
  chatHelpers.handleSubmit = useCallback(async (...args) => {
    const [message, options = {}] = args;
    const newOptions = {
      ...options,
      headers: {
        ...options.headers,
        'x-project-id': currentProjectId
      }
    };
    return originalSubmit(message, newOptions);
  }, [originalSubmit, currentProjectId]);

  const addedChatHelpers = useAddedResponse({ rootIndex: index });

  useSSE(rootSubmission, chatHelpers, false);
  useSSE(addedSubmission, addedChatHelpers, true);

  const methods = useForm<ChatFormValues>({
    defaultValues: { text: '' },
  });

  let content: JSX.Element | null | undefined;
  if (isLoading && conversationId !== 'new') {
    content = (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="opacity-0" />
      </div>
    );
  } else if (messagesTree && messagesTree.length !== 0) {
    content = (
      <>
        <div className="mb-4 flex justify-end px-4">
          <ProjectSelector onSelect={setCurrentProjectId} />
        </div>
        <MessagesView messagesTree={messagesTree} Header={<Header />} />
      </>
    );
  } else {
    content = (
      <>
        <div className="mb-4 flex justify-end px-4">
          <ProjectSelector onSelect={setCurrentProjectId} />
        </div>
        <Landing Header={<Header />} />
      </>
    );
  }

  return (
    <ChatFormProvider {...methods}>
      <ChatContext.Provider value={chatHelpers}>
        <AddedChatContext.Provider value={addedChatHelpers}>
          <Presentation>
            {content}
            <div className="w-full border-t-0 pl-0 pt-2 dark:border-white/20 md:w-[calc(100%-.5rem)] md:border-t-0 md:border-transparent md:pl-0 md:pt-0 md:dark:border-transparent">
              <ChatForm index={index} />
              <Footer />
            </div>
          </Presentation>
        </AddedChatContext.Provider>
      </ChatContext.Provider>
    </ChatFormProvider>
  );
}

export default memo(ChatView);