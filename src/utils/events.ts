/**
 * Custom event utilities for inter-component communication.
 * Provides type-safe event dispatching and listening.
 */

export namespace AppEvents {
  export const OPEN_SYNTHESIS_WORKBENCH = 'open-synthesis-workbench';
  export const OPEN_WWC_COPILOT = 'open-wwc-copilot';

  export interface IOpenSynthesisWorkbenchDetail {
    paperIds: number[];
  }

  export interface IOpenWWCCopilotDetail {
    paperId: number;
    paperTitle: string;
  }

  /**
   * Dispatch event to open synthesis workbench.
   */
  export function dispatchOpenSynthesisWorkbench(paperIds: number[]): void {
    window.dispatchEvent(
      new CustomEvent<IOpenSynthesisWorkbenchDetail>(OPEN_SYNTHESIS_WORKBENCH, {
        detail: { paperIds }
      })
    );
  }

  /**
   * Dispatch event to open WWC Co-Pilot.
   */
  export function dispatchOpenWWCCopilot(
    paperId: number,
    paperTitle: string
  ): void {
    window.dispatchEvent(
      new CustomEvent<IOpenWWCCopilotDetail>(OPEN_WWC_COPILOT, {
        detail: { paperId, paperTitle }
      })
    );
  }

  /**
   * Listen for open synthesis workbench events.
   * @returns Cleanup function to remove listener
   */
  export function onOpenSynthesisWorkbench(
    handler: (detail: IOpenSynthesisWorkbenchDetail) => void
  ): () => void {
    const listener = ((event: CustomEvent<IOpenSynthesisWorkbenchDetail>) => {
      handler(event.detail);
    }) as EventListener;

    window.addEventListener(OPEN_SYNTHESIS_WORKBENCH, listener);
    return () => window.removeEventListener(OPEN_SYNTHESIS_WORKBENCH, listener);
  }

  /**
   * Listen for open WWC Co-Pilot events.
   * @returns Cleanup function to remove listener
   */
  export function onOpenWWCCopilot(
    handler: (detail: IOpenWWCCopilotDetail) => void
  ): () => void {
    const listener = ((event: CustomEvent<IOpenWWCCopilotDetail>) => {
      handler(event.detail);
    }) as EventListener;

    window.addEventListener(OPEN_WWC_COPILOT, listener);
    return () => window.removeEventListener(OPEN_WWC_COPILOT, listener);
  }
}
